# Home Assistant ETA Integration

An Home Assistant integration for fetching data from the api endpoint exposed by the ETA heating system in your local network.

<img src="eta-heiztechnik-gmbh-logo-vector.png" alt="Eta Heiztechnik Logo" width="400"/>

> Disclaimer: This repository is based on the [integration_bluepring](https://github.com/ludeeus/integration_blueprint) by [@ludeeus](https://github.com/ludeeus) and the [homeassistant_eta_integration](https://github.com/nigl/homeassistant_eta_integration) developed by [@nigl](https://github.com/nigl).

## What is it about?

The ETA heating system exposes an api endpoint in your local network that can be used to fetch data from the system and even control certain elements of the system.
This integration is enabling you to fetch data from it such as temperatures, power values and on/off states.

To use the functionality, you have to enable the api endpoint.
Take a look in the [api documentation](ETA-RESTful-v1.2.pdf) for more information about enabling and the individual options the api provides.

## How to configure the integration

The configuration of the integration consists of two steps and some preparation work.

**Preparation:** I recommend taking a look at the menu provided by the api at the url `<ip>:<port>/user/menu` to get a basic overview of the available endpoints.
Not all listed endpoints can be polled for information and not all pollable endpoints return valuable information.
As a general rule, I'd fetch the value for each point you're interested at least once to check if the datapoint has a unit.
You can fetch a datapoint by using the url `<ip>:<port>/user/var/<object-uri>`, where the `object-uri` can be obtained from the menu.

> Fetching datapoints without units is not fully supported by the integration at the moment and thus, I'd stick with values that have a unit such as `°C` or `W`.
> Some unit-less values are supported, e.g. `Ein`, `Aus`, `Eingeschaltet` and `Ausgeschaltet` to support basic on/off monitoring.

After collection the datapoints and full names (the whole name path to the object, e.g. `Buffer.Inputs.Buffer Sensor 1`) of the datapoints you're interested, you can start configuring the integration.

**Configuration of the integration:** The integration will ask you for the IP address and the port of your ETA system.
It then will fetch the menu and present you with a list of all available (including non pollable and useless) endpoints.
Select the endpoints that you've evaluated as valuable during the **preparation step**.

## Information on this repository

This repository contains multiple files, here is a overview:

File | Purpose | Documentation
-- | -- | --
`.devcontainer.json` | Used for development/testing with Visual Studio Code. | [Documentation](https://code.visualstudio.com/docs/remote/containers)
`custom_components/eta_heating_technology/*` | Integration files, this is where everything happens. | [Documentation](https://developers.home-assistant.io/docs/creating_component_index)
`CONTRIBUTING.md` | Guidelines on how to contribute. | [Documentation](https://help.github.com/en/github/building-a-strong-community/setting-guidelines-for-repository-contributors)
`LICENSE` | The license file for the project. | [Documentation](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/licensing-a-repository)
`README.md` | The file you are reading now, should contain info about the integration, installation and configuration instructions. | [Documentation](https://help.github.com/en/github/writing-on-github/basic-writing-and-formatting-syntax)
`requirements.txt` | Python packages used for development/lint/testing this integration. | [Documentation](https://pip.pypa.io/en/stable/user_guide/#requirements-files)

To start a development instance of the integration, run the `scripts/develop` to start HA and test out your new integration.

## FAQ and Problems

- I've encountered a problem in which the [XML parsing](https://pydantic-xml.readthedocs.io/en/latest/pages/misc.html#xml-parser) was throwing exceptions because the it used `lxml` instead of `xml.etree.ElementTree` for parsing.
  The solution is to set the environment variable `FORCE_STD_XML` to `True` using [hass-environment-variable](https://github.com/Athozs/hass-environment-variable).
