// var G2 = artifacts.require("./libraries/BN256G2");
// var bnCurve = artifacts.require("./libraries/G");
// var Request = artifacts.require("./contracts/Request");
// var Params = artifacts.require("./contracts/Params");
// var Verify = artifacts.require("./contracts/Verify");
// var Opening = artifacts.require("./contracts/Opening");
// var Issue = artifacts.require("./contracts/Issue");

// module.exports = function (deployer) {

//   deployer.deploy(G2, {from: "0xc804EFd57ae0038d46Dd9d9225Ece639D3098E66"});
//   deployer.link(G2, bnCurve);
//   deployer.deploy(bnCurve, {from: "0xc804EFd57ae0038d46Dd9d9225Ece639D3098E66"});
  
//   deployer.link(bnCurve, Verify);
//   deployer.link(G2, Verify);
//   deployer.deploy(Verify, {from: "0x9017224b425135EF21DaD7b61E1C8DDEaf1D5034"});

//   deployer.link(bnCurve, Params);
//   deployer.deploy(Params, {from: "0xc804EFd57ae0038d46Dd9d9225Ece639D3098E66"});
  
//   deployer.link(bnCurve, Request);
//   deployer.link(G2, Request);
//   deployer.deploy(Request, {from: "0xc804EFd57ae0038d46Dd9d9225Ece639D3098E66"});

//   deployer.deploy(Issue, {from: "0xc804EFd57ae0038d46Dd9d9225Ece639D3098E66"});

//   deployer.deploy(Opening, {from: "0xc804EFd57ae0038d46Dd9d9225Ece639D3098E66"});

// };


var G2 = artifacts.require("./libraries/BN256G2");
var BnCurve = artifacts.require("./libraries/G");
var Request = artifacts.require("./contracts/Request");
var Params = artifacts.require("./contracts/Params");
var Verify = artifacts.require("./contracts/Verify");
var Opening = artifacts.require("./contracts/Opening");
var Issue = artifacts.require("./contracts/Issue");
var Accumulator = artifacts.require("./contracts/Accumulator");


module.exports = async function (deployer) {

  await deployer.deploy(G2, {from: "0x6419B5373E351607530192844f47d36263F16d68"});
  const g2 = await G2.deployed()

  await deployer.link(G2, BnCurve);
  await deployer.deploy(BnCurve, {from: "0x6419B5373E351607530192844f47d36263F16d68"});
  const bnCurve = await BnCurve.deployed()

  await deployer.link(BnCurve, Params);
  await deployer.deploy(Params, {from: "0x6419B5373E351607530192844f47d36263F16d68"});
  const params = await Params.deployed()

  // await Verify.detectNetwork();
  await deployer.link(BnCurve, Verify);
  await deployer.link(G2, Verify);
  await deployer.deploy(Verify, params.address, {from: "0x0f166ee382eA8aaA1E48F319c7c4EF4656f23dd2"});
  const verify = await Verify.deployed()
  
  await deployer.link(G2, Accumulator);
  await deployer.deploy(Accumulator, {from: "0x6419B5373E351607530192844f47d36263F16d68"});
  const accumulator = await Accumulator.deployed()

  await deployer.link(BnCurve, Request);
  await deployer.link(G2, Request);
  await deployer.deploy(Request, params.address,accumulator.address, {from: "0x6419B5373E351607530192844f47d36263F16d68"});
  const request = await Request.deployed()

  await deployer.deploy(Issue, params.address, {from: "0x6419B5373E351607530192844f47d36263F16d68"});
  const issue = await Issue.deployed()

  await deployer.deploy(Opening, params.address, {from: "0x6419B5373E351607530192844f47d36263F16d68"});
  const opening = await Opening.deployed()

  console.log(opening.address);
  console.log(issue.address);
  console.log(request.address);
  console.log(params.address);
  console.log(verify.address);
  console.log(accumulator.address)
};