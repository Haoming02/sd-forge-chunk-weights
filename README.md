# SD Forge Chunk Weights
This is an Extension for [Forge Classic](https://github.com/Haoming02/sd-webui-forge-classic), which allows you to control the weighting for each chunk of prompts *(**i.e.** every 75 tokens)*.

> [!Tip]
> In the WebUI, you can use the keyword **`BREAK`** to manually separate prompts into different chunks to group similar concepts together

## How to Use
In the `Weighting` text field, enter a list of **comma-separated floats**, corresponding to the weights of each chunk in order *(the default weight is `1.0`)*

## Examples

<table>
    <tr align="center">
        <td>
            <img src="./example/1.jpg" width=384><br>
            a photo of a dog, a house<br>
            <b>Extension:</b> <code>Disabled</code>
        </td>
        <td>
            <img src="./example/2.jpg" width=384><br>
            a photo of a dog, BREAK, a house<br>
            <b>Extension:</b> <code>Disabled</code>
        </td>
    </tr>
    <tr align="center">
        <td>
            <img src="./example/3.jpg" width=384><br>
            a photo of a dog, BREAK, a house<br>
            <b>Weights:</b> <code>1.5, 1.0</code>
        </td>
        <td>
            <img src="./example/4.jpg" width=384><br>
            a photo of a dog, BREAK, a house<br>
            <b>Weights:</b> <code>1.0, 1.5</code>
        </td>
    </tr>
</table>

<hr>

- Idea by. **[@jeanhadrien](https://github.com/jeanhadrien)** in [#89](https://github.com/Haoming02/sd-webui-forge-classic/issues/89), based on this [Extension](https://github.com/klimaleksus/stable-diffusion-webui-embedding-merge/)
