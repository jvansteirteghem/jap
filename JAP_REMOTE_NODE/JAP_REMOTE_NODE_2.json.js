module.exports = 
{
	"REMOTE_PROXY_SERVER":
	{
		"TYPE": "HTTPS",
		"ADDRESS": "127.0.0.1",
		"PORT": 443,
		"AUTHENTICATION":
		[
			{
				"USERNAME": "1",
				"PASSWORD": "1"
			},
			{
				"USERNAME": "2",
				"PASSWORD": "2"
			}
		],
		"CERTIFICATE":
		{
			"KEY":
			{
				"FILE": "CK.pem"
			},
			"FILE": "C.pem"
		}
	}
}