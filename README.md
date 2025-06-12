# SD Forge Chunk Weights
This is an Extension for [Forge Classic](https://github.com/Haoming02/sd-webui-forge-classic), which allows you to control the weighting of each prompt chunk *(**i.e.** every 75 tokens)*. 

<p align="right"><b>W.I.P</b></p>

## Features

In the WebUI, you can use the keyword **`BREAK`** to manually separate prompts into different chunks. This Extension adds a text field that also allows you to specify the weighting of each chunk.

> [!Important]
> Does **not** work when `Persistent Cond Cache` is also enabled, unless you edit the prompts again

## How to Use
In the text field, enter a list of **comma-separated floats**, cooresponding to the weights of each chunk in order *(the default weight is `1.0`)*

## Examples

<table>
<tr>
    <th>Result</th>
    <th>Prompt</th>
    <th>Weights</th>
</tr>
<tr>
    <td><img src="./example/1.jpg" width=128></td>
    <td>a photo of a dog, a house</td>
    <td>N/A</td>
</tr>
<tr>
    <td><img src="./example/2.jpg" width=128></td>
    <td>a photo of a dog, BREAK, a house</td>
    <td>N/A</td>
</tr>
<tr>
    <td><img src="./example/3.jpg" width=128></td>
    <td>a photo of a dog, BREAK, a house</td>
    <td>1.5, 1.0</td>
</tr>
<tr>
    <td><img src="./example/4.jpg" width=128></td>
    <td>a photo of a dog, BREAK, a house</td>
    <td>1.0, 1.5</td>
</tr>
</table>

## ToDo

- [ ] Validation

> [!Important]
> Currently, the Extension does not validate the inputs, make sure you enter the correct number of weights yourself

- [ ] Logging
- [ ] Infotext

<hr>

- Idea by. **[@jeanhadrien](https://github.com/jeanhadrien)** in [#89](https://github.com/Haoming02/sd-webui-forge-classic/issues/89), based on this [Extension](https://github.com/klimaleksus/stable-diffusion-webui-embedding-merge/) 
