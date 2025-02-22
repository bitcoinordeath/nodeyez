# ![Nodeyez](../images/nodeyez.svg)
Display panels to get the most from your node

## Whirlpool Liquidity

This script calls an API to get the whirlpool pool status indicating the number
of premixers and remixers in each pool and then displays a summary panel of
the information.

![sample whirlpool liquidity display](../images/whirlpoolliquidity.png)

* To run this script

   ```sh
   cd /home/nodeyez/nodeyez/scripts
   /home/nodeyez/nodeyez/scripts/whirlpoolliquidity.py
   ```

   Press CTRL+C to stop the process

* To configure this script

   Override the default configuration as follows

   ```sh
   nano /home/nodeyez/nodeyez/config/whirlpoolliquidity.json
   ```

   | field name | description |
   | --- | --- |
   | outputFile | The path to save the generated image. Default `/home/nodeyez/nodeyez/imageoutput/whirlpoolliquidity.png` |
   | width | The width, in pixels, to generate the image. Default `480` |
   | height | The height, in pixels, to generate the image. Default `320` |
   | sleepInterval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `3600` |
   | useTor | Indicates whether remote calls should use tor for privacy. This should not be used for internal/local addresses such as access to whirlpool cli on same system. Experimental. Default `true` |
   | isTrusted | Indicates whether the whirlpoolurl should be considered trusted and skip certificate verification. Should only be used for local dojo and whirlpool cli instances using self-signed certificate. Default `false` |
   | whirlpoolurl | The url to use for retrieving pool information from whirlpool instance. If you have a local dojo with whirlpool-cli, you may use that server here.  For example, for MyNodeBTC, you can use `https://127.0.0.1:8899`.  Default: `http://udkmfc5j6zvv3ysavbrwzhwji4hpyfe3apqa6yst7c7l32mygf65g4ad.onion` |
   | apiKey | If you are using a local dojo and whirlpool cli, you must specify the apiKey for communicating with it.  For MyNodeBTC, you can find this on the info page for Whirlpool as the API Key for Whirlpool GUI. Default _none_ |
   | colorBackground | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
   | colorHeader | The color of the text expressed as a Hexadecial color specifier. Default `#ffffff` |
   | colorPoolHeader | The color to use for the individual pool header expressed as a Hexadecimal color specifier. Default `#aa2222` |
   | colorRemixers | The color of the text label for remixers expressed as a Hexadecimal color specifier. Default `#aaaaaa` |
   | colorPremixers | The color of the text label for premixers expressed as a Hexadecimal color specifier. Default `#aaaaaa` |
   | colorElapsed | The color of the text label for elapsed time expressed as a Hexadecimal color specifier. Default `#aaaaaa` |
   | colorTextFG | The color of all other text labels and values expressed as a Hexadecimal color specifier. Default `#ffffff` |

   After making changes, Save (CTRL+O) and Exit (CTRL+X) nano.


---

[Home](../README.md) | 

