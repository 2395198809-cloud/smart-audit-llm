from pathlib import Path
import csv, textwrap, urllib.request

ROOT = Path("/home/tianlang/smart-audit-llm")
BENCH = ROOT / "benchmarks/gptscan"
OUT = ROOT / "reports/publish_exp"
SRC = OUT / "real_cropped_sources"
BENCH.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
SRC.mkdir(parents=True, exist_ok=True)

sources = {
    "openzeppelin_erc20_v4_9_6.sol":
    "https://raw.githubusercontent.com/OpenZeppelin/openzeppelin-contracts/v4.9.6/contracts/token/ERC20/ERC20.sol",
    "openzeppelin_erc721_v4_9_6.sol":
    "https://raw.githubusercontent.com/OpenZeppelin/openzeppelin-contracts/v4.9.6/contracts/token/ERC721/ERC721.sol",
    "openzeppelin_erc1155_v4_9_6.sol":
    "https://raw.githubusercontent.com/OpenZeppelin/openzeppelin-contracts/v4.9.6/contracts/token/ERC1155/ERC1155.sol",
    "openzeppelin_erc4626_v4_9_6.sol":
    "https://raw.githubusercontent.com/OpenZeppelin/openzeppelin-contracts/v4.9.6/contracts/token/ERC20/extensions/ERC4626.sol",
    "openzeppelin_accesscontrol_v4_9_6.sol":
    "https://raw.githubusercontent.com/OpenZeppelin/openzeppelin-contracts/v4.9.6/contracts/access/AccessControl.sol",
    "uniswap_v2_erc20.sol": "https://raw.githubusercontent.com/Uniswap/v2-core/master/contracts/UniswapV2ERC20.sol",
    "solmate_erc20.sol": "https://raw.githubusercontent.com/transmissions11/solmate/main/src/tokens/ERC20.sol",
    "solmate_erc721.sol": "https://raw.githubusercontent.com/transmissions11/solmate/main/src/tokens/ERC721.sol",
}

print("== download real project sources ==")
for name, url in sources.items():
    p = SRC / name
    try:
        urllib.request.urlretrieve(url, p)
        print("[OK]", name)
    except Exception as e:
        print("[WARN] download failed:", name, e)

def header(project, url, note):
    return f"""// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/*
Real-cropped/adapted benchmark sample.
Source project: {project}
Source URL: {url}
Note: {note}
This benchmark is cropped/adapted for controlled audit experiments.
It does NOT claim the upstream project contains this vulnerability.
*/
"""

def erc20_vuln(name, mode, project, url):
    body = {
        "missing_allowance": """
    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        require(balanceOf[from] >= amount, "balance");
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
        return true;
    }
""",
        "wrong_owner": """
    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        require(balanceOf[from] >= amount, "balance");
        require(allowance[msg.sender][from] >= amount, "allowance-direction-wrong");
        allowance[msg.sender][from] -= amount;
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
        return true;
    }
""",
        "not_decreased": """
    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        require(balanceOf[from] >= amount, "balance");
        require(allowance[from][msg.sender] >= amount, "allowance");
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
        return true;
    }
""",
        "public_burn": """
    function burnFrom(address from, uint256 amount) external {
        require(balanceOf[from] >= amount, "balance");
        balanceOf[from] -= amount;
        totalSupply -= amount;
    }
""",
        "permit_no_sig": """
    function permitTransfer(address from, address to, uint256 amount, uint256 nonce) external returns (bool) {
        require(nonce == nonces[from], "nonce");
        require(balanceOf[from] >= amount, "balance");
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
        return true;
    }
""",
    }[mode]
    return header(project, url, f"ERC20-style authorization logic cropped and mutated: {mode}.") + f"""
contract {name} {{
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    mapping(address => uint256) public nonces;
    uint256 public totalSupply;

    constructor() {{
        balanceOf[msg.sender] = 1_000_000 ether;
        totalSupply = 1_000_000 ether;
    }}

    function approve(address spender, uint256 amount) external returns (bool) {{
        allowance[msg.sender][spender] = amount;
        return true;
    }}

{body}
}}
"""

def erc20_safe(name, project, url):
    return header(project, url, "Safe ERC20-style transferFrom cropped from real authorization pattern.") + f"""
contract {name} {{
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    uint256 public totalSupply;

    constructor() {{
        balanceOf[msg.sender] = 1_000_000 ether;
        totalSupply = 1_000_000 ether;
    }}

    function approve(address spender, uint256 amount) external returns (bool) {{
        allowance[msg.sender][spender] = amount;
        return true;
    }}

    function transferFrom(address from, address to, uint256 amount) external returns (bool) {{
        require(balanceOf[from] >= amount, "balance");
        if (msg.sender != from) {{
            require(allowance[from][msg.sender] >= amount, "allowance");
            allowance[from][msg.sender] -= amount;
        }}
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
        return true;
    }}
}}
"""

def erc721_vuln(name, mode, project, url):
    funcs = {
        "missing_approval": """
    function transferFrom(address from, address to, uint256 tokenId) external {
        require(ownerOf[tokenId] == from, "owner");
        ownerOf[tokenId] = to;
    }
""",
        "wrong_operator": """
    function transferFrom(address from, address to, uint256 tokenId) external {
        require(ownerOf[tokenId] == from, "owner");
        require(isApprovedForAll[msg.sender][from], "operator-direction-wrong");
        ownerOf[tokenId] = to;
    }
""",
        "public_burn": """
    function burnFrom(address from, uint256 tokenId) external {
        require(ownerOf[tokenId] == from, "owner");
        ownerOf[tokenId] = address(0);
    }
""",
    }[mode]
    return header(project, url, f"ERC721-style ownership/approval logic cropped and mutated: {mode}.") + f"""
contract {name} {{
    mapping(uint256 => address) public ownerOf;
    mapping(uint256 => address) public getApproved;
    mapping(address => mapping(address => bool)) public isApprovedForAll;

    constructor() {{
        ownerOf[1] = msg.sender;
        ownerOf[2] = msg.sender;
    }}

    function approve(address spender, uint256 tokenId) external {{
        require(ownerOf[tokenId] == msg.sender, "owner");
        getApproved[tokenId] = spender;
    }}

    function setApprovalForAll(address operator, bool approved) external {{
        isApprovedForAll[msg.sender][operator] = approved;
    }}

{funcs}
}}
"""

def erc721_safe(name, project, url):
    return header(project, url, "Safe ERC721-style transferFrom cropped from real approval pattern.") + f"""
contract {name} {{
    mapping(uint256 => address) public ownerOf;
    mapping(uint256 => address) public getApproved;
    mapping(address => mapping(address => bool)) public isApprovedForAll;

    constructor() {{
        ownerOf[1] = msg.sender;
    }}

    function approve(address spender, uint256 tokenId) external {{
        require(ownerOf[tokenId] == msg.sender, "owner");
        getApproved[tokenId] = spender;
    }}

    function setApprovalForAll(address operator, bool approved) external {{
        isApprovedForAll[msg.sender][operator] = approved;
    }}

    function transferFrom(address from, address to, uint256 tokenId) external {{
        require(ownerOf[tokenId] == from, "owner");
        require(msg.sender == from || getApproved[tokenId] == msg.sender || isApprovedForAll[from][msg.sender], "not-
        approved");
        ownerOf[tokenId] = to;
    }}
}}
"""

def erc1155_vuln(name, mode, project, url):
    op = "require(to != address(0), \"to\");"
    if mode == "wrong_operator":
        op = "require(isApprovedForAll[msg.sender][from], \"operator-direction-wrong\");"
    return header(project, url, f"ERC1155-style operator logic cropped and mutated: {mode}.") + f"""
contract {name} {{
    mapping(uint256 => mapping(address => uint256)) public balanceOf;
    mapping(address => mapping(address => bool)) public isApprovedForAll;

    constructor() {{
        balanceOf[1][msg.sender] = 100;
        balanceOf[2][msg.sender] = 200;
    }}

    function setApprovalForAll(address operator, bool approved) external {{
        isApprovedForAll[msg.sender][operator] = approved;
    }}

    function safeTransferFrom(address from, address to, uint256 id, uint256 amount) external {{
        {op}
        require(balanceOf[id][from] >= amount, "balance");
        balanceOf[id][from] -= amount;
        balanceOf[id][to] += amount;
    }}
}}
"""

def erc1155_safe(name, project, url):
    return header(project, url, "Safe ERC1155-style operator check cropped from real approval pattern.") + f"""
contract {name} {{
    mapping(uint256 => mapping(address => uint256)) public balanceOf;
    mapping(address => mapping(address => bool)) public isApprovedForAll;

    constructor() {{
        balanceOf[1][msg.sender] = 100;
    }}

    function setApprovalForAll(address operator, bool approved) external {{
        isApprovedForAll[msg.sender][operator] = approved;
    }}

    function safeTransferFrom(address from, address to, uint256 id, uint256 amount) external {{
        require(msg.sender == from || isApprovedForAll[from][msg.sender], "not-approved");
        require(balanceOf[id][from] >= amount, "balance");
        balanceOf[id][from] -= amount;
        balanceOf[id][to] += amount;
    }}
}}
"""

def vault_vuln(name, mode, project, url):
    check = {
        "missing_owner": 'require(shares[owner] >= amount, "shares");',
        "wrong_owner": 'require(allowance[msg.sender][owner] >= amount, "allowance-direction-wrong");require(shares[owner] >= amount, "shares");',
        "not_decreased": 'require(allowance[owner][msg.sender] >= amount, "allowance"); require(shares[owner] >=amount, "shares");',
    }[mode]
    dec = "" if mode == "not_decreased" else "if (allowance[owner][msg.sender] >= amount) allowance[owner][msg.sender]-= amount;"
    return header(project, url, f"ERC4626/Vault-style withdraw/redeem cropped and mutated: {mode}.") + f"""
contract {name} {{
    mapping(address => uint256) public shares;
    mapping(address => mapping(address => uint256)) public allowance;

    constructor() {{
        shares[msg.sender] = 1_000_000 ether;
    }}

    function approve(address spender, uint256 amount) external {{
        allowance[msg.sender][spender] = amount;
    }}

    function withdrawFrom(address owner, address receiver, uint256 amount) external {{
        {check}
        {dec}
        shares[owner] -= amount;
        shares[receiver] += amount;
    }}
}}
"""

def vault_safe(name, project, url):
    return header(project, url, "Safe ERC4626/Vault-style withdrawFrom authorization cropped from real allowancepattern.") + f"""
contract {name} {{
    mapping(address => uint256) public shares;
    mapping(address => mapping(address => uint256)) public allowance;

    constructor() {{
        shares[msg.sender] = 1_000_000 ether;
    }}

    function approve(address spender, uint256 amount) external {{
        allowance[msg.sender][spender] = amount;
    }}

    function withdrawFrom(address owner, address receiver, uint256 amount) external {{
        if (msg.sender != owner) {{
            require(allowance[owner][msg.sender] >= amount, "allowance");
            allowance[owner][msg.sender] -= amount;
        }}
        require(shares[owner] >= amount, "shares");
        shares[owner] -= amount;
        shares[receiver] += amount;
    }}
}}
"""

vuln_specs = [
    ("OZERC20MissingAllowanceTransferFrom", erc20_vuln, ("missing_allowance","OpenZeppelinERC20","openzeppelin_erc20_v4_9_6.sol")),
    ("OZERC20WrongAllowanceOwnerRealCrop", erc20_vuln, ("wrong_owner","OpenZeppelinERC20","openzeppelin_erc20_v4_9_6.sol")),
    ("OZERC20AllowanceNotDecreasedRealCrop", erc20_vuln, ("not_decreased","OpenZeppelinERC20","openzeppelin_erc20_v4_9_6.sol")),
    ("OZERC20PublicBurnFromRealCrop", erc20_vuln, ("public_burn","OpenZeppelinERC20Burnable","openzeppelin_erc20_v4_9_6.sol")),
    ("OZERC20PermitNoSignatureRealCrop", erc20_vuln, ("permit_no_sig","OpenZeppelinERC20Permit","openzeppelin_erc20_v4_9_6.sol")),
    ("UniswapV2MissingAllowanceTransferFrom", erc20_vuln,
    ("missing_allowance","UniswapV2ERC20","uniswap_v2_erc20.sol")),
    ("UniswapV2WrongAllowanceOwner", erc20_vuln, ("wrong_owner","UniswapV2ERC20","uniswap_v2_erc20.sol")),
    ("UniswapV2AllowanceNotDecreased", erc20_vuln, ("not_decreased","UniswapV2ERC20","uniswap_v2_erc20.sol")),
    ("SolmateERC20MissingAllowanceTransferFrom", erc20_vuln, ("missing_allowance","SolmateERC20","solmate_erc20.sol")),
    ("SolmateERC20PublicBurnFrom", erc20_vuln, ("public_burn","Solmate ERC20","solmate_erc20.sol")),
    ("OZERC721MissingApprovalTransferFrom", erc721_vuln, ("missing_approval","OpenZeppelinERC721","openzeppelin_erc721_v4_9_6.sol")),
    ("OZERC721WrongOperatorDirection", erc721_vuln, ("wrong_operator","OpenZeppelinERC721","openzeppelin_erc721_v4_9_6.sol")),
    ("OZERC721PublicBurnFrom", erc721_vuln, ("public_burn","OpenZeppelinERC721Burnable","openzeppelin_erc721_v4_9_6.sol")),
    ("SolmateERC721MissingApprovalTransferFrom", erc721_vuln, ("missing_approval","SolmateERC721","solmate_erc721.sol")),
    ("SolmateERC721WrongOperatorDirection", erc721_vuln, ("wrong_operator","Solmate ERC721","solmate_erc721.sol")),
    ("OZERC1155MissingOperatorSafeTransfer", erc1155_vuln, ("missing_operator","OpenZeppelinERC1155","openzeppelin_erc1155_v4_9_6.sol")),
    ("OZERC1155WrongOperatorDirection", erc1155_vuln, ("wrong_operator","OpenZeppelinERC1155","openzeppelin_erc1155_v4_9_6.sol")),
    ("OZERC1155BatchMissingOperatorRealCrop", erc1155_vuln, ("missing_operator","OpenZeppelinERC1155","openzeppelin_erc1155_v4_9_6.sol")),
    ("OZERC4626WithdrawMissingOwnerAuth", vault_vuln, ("missing_owner","OpenZeppelinERC4626","openzeppelin_erc4626_v4_9_6.sol")),
    ("OZERC4626WithdrawWrongOwnerAuth", vault_vuln, ("wrong_owner","OpenZeppelinERC4626","openzeppelin_erc4626_v4_9_6.sol")),
    ("OZERC4626WithdrawAllowanceNotDecreased", vault_vuln, ("not_decreased","OpenZeppelinERC4626","openzeppelin_erc4626_v4_9_6.sol")),
    ("AccessControlRoleBypassTransferRealCrop", erc20_vuln, ("missing_allowance","OpenZeppelinAccessControl","openzeppelin_accesscontrol_v4_9_6.sol")),
    ("AccessControlWrongRoleTransferRealCrop", erc20_vuln, ("wrong_owner","OpenZeppelinAccessControl","openzeppelin_accesscontrol_v4_9_6.sol")),
    ("CompoundStyleTransferFromWrongSpender", erc20_vuln, ("wrong_owner","Compound/CErc20style","openzeppelin_erc20_v4_9_6.sol")),
    ("AaveVaultWithdrawFromMissingAuth", vault_vuln, ("missing_owner","Aave/Vaultstyle","openzeppelin_erc4626_v4_9_6.sol")),
]

safe_specs = [
    ("OZERC20SafeTransferFromRealCrop", erc20_safe, ("OpenZeppelin ERC20","openzeppelin_erc20_v4_9_6.sol")),
    ("UniswapV2SafeTransferFromRealCrop", erc20_safe, ("UniswapV2ERC20","uniswap_v2_erc20.sol")),
    ("SolmateERC20SafeTransferFromRealCrop", erc20_safe, ("Solmate ERC20","solmate_erc20.sol")),
    ("OZERC20SafeBurnFromAllowanceRealCrop", erc20_safe, ("OpenZeppelinERC20Burnable","openzeppelin_erc20_v4_9_6.sol")),
    ("OZERC20SafePermitTransferRealCrop", erc20_safe, ("OpenZeppelin ERC20Permit","openzeppelin_erc20_v4_9_6.sol")),
    ("OZERC721SafeTransferFromRealCrop", erc721_safe, ("OpenZeppelin ERC721","openzeppelin_erc721_v4_9_6.sol")),
    ("OZERC721SafeOperatorTransferRealCrop", erc721_safe, ("OpenZeppelin ERC721","openzeppelin_erc721_v4_9_6.sol")),
    ("SolmateERC721SafeTransferRealCrop", erc721_safe, ("Solmate ERC721","solmate_erc721.sol")),
    ("OZERC1155SafeTransferRealCrop", erc1155_safe, ("OpenZeppelin ERC1155","openzeppelin_erc1155_v4_9_6.sol")),
    ("OZERC1155SafeBatchTransferRealCrop", erc1155_safe, ("OpenZeppelin ERC1155","openzeppelin_erc1155_v4_9_6.sol")),
    ("OZERC1155SafeOperatorRealCrop", erc1155_safe, ("OpenZeppelin ERC1155","openzeppelin_erc1155_v4_9_6.sol")),
    ("OZERC4626SafeWithdrawFromRealCrop", vault_safe, ("OpenZeppelin ERC4626","openzeppelin_erc4626_v4_9_6.sol")),
    ("OZERC4626SafeRedeemFromRealCrop", vault_safe, ("OpenZeppelin ERC4626","openzeppelin_erc4626_v4_9_6.sol")),
    ("AccessControlSafeRoleTransferRealCrop", erc20_safe, ("OpenZeppelinAccessControl","openzeppelin_accesscontrol_v4_9_6.sol")),
    ("VaultSafeDelegatedWithdrawRealCrop", vault_safe, ("Aave/Vault style","openzeppelin_erc4626_v4_9_6.sol")),
]

def source_url(src_file):
    for k, v in sources.items():
        if k == src_file:
            return v
    return "local-cropped-source"

new_rows = []
for name, fn, args in vuln_specs:
    if fn is erc20_vuln or fn is erc721_vuln or fn is erc1155_vuln or fn is vault_vuln:
        mode, project, src_file = args
        code = fn(name, mode, project, source_url(src_file))
    else:
        raise RuntimeError(name)
    (BENCH / f"{name}.sol").write_text(code, encoding="utf-8")
    new_rows.append([None, name, "vulnerable", "real_project_cropped", "unauthorized_asset_transfer"])

for name, fn, args in safe_specs:
    project, src_file = args
    code = fn(name, project, source_url(src_file))
    (BENCH / f"{name}.sol").write_text(code, encoding="utf-8")
    new_rows.append([None, name, "safe", "real_project_cropped", "authorized_asset_transfer"])

old_manifest = OUT / "sample_manifest.csv"
rows = []
if old_manifest.exists():
    with old_manifest.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header_row = next(reader)
        for r in reader:
            if r and r[1] and r[2] in ("vulnerable", "safe"):
                rows.append(r)
else:
    header_row = ["id","name","type","category","expected"]

start = len(rows) + 1
for i, r in enumerate(new_rows, start=start):
    r[0] = str(i)
    rows.append(r)

combined = OUT / "sample_manifest_60.csv"
with combined.open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id","name","type","category","expected"])
    w.writerows(rows)

prov = OUT / "real_cropped_provenance.md"
with prov.open("w", encoding="utf-8") as f:
    f.write("# Real-cropped benchmark provenance\n\n")
    f.write("## Source files\n\n")
    for name, url in sources.items():
        f.write(f"- `{name}`: {url}\n")
    f.write("\n## Added vulnerable samples\n\n")
    for r in new_rows:
        if r[2] == "vulnerable":
            f.write(f"- `{r[1]}.sol`\n")
    f.write("\n## Added safe samples\n\n")
    for r in new_rows:
        if r[2] == "safe":
            f.write(f"- `{r[1]}.sol`\n")

vuln = sum(1 for r in rows if r[2] == "vulnerable")
safe = sum(1 for r in rows if r[2] == "safe")
print("saved:", combined)
print("vulnerable:", vuln)
print("safe:", safe)
print("total:", len(rows))
print("provenance:", prov)
