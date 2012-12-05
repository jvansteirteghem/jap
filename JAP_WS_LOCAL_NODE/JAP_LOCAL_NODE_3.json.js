module.exports = 
{
	"LOCAL_PROXY_SERVER":
	{
		"ADDRESS": "127.0.0.1",
		"PORT": 1080
	},
	"REMOTE_PROXY_SERVERS":
	[
		{
			"TYPE": "HTTP",
			"ADDRESS": "127.0.0.1",
			"PORT": 80,
			"AUTHENTICATION":
			{
				"USERNAME": "1",
				"PASSWORD": "1"
			}
		},
		{
			"TYPE": "HTTPS",
			"ADDRESS": "127.0.0.1",
			"PORT": 443,
			"AUTHENTICATION":
			{
				"USERNAME": "1",
				"PASSWORD": "1"
			},
			"CERTIFICATE":
			{
				"AUTHENTICATION":
				{
					"FILE": "CA.pem"
				}
			}
		}
	],
	"PROXY_SERVER":
	{
		"ADDRESS": "127.0.0.1",
		"PORT": 8080,
		"AUTHENTICATION":
		{
			"USERNAME": "1",
			"PASSWORD": "1"
		}
	}
}