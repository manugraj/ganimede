def pkg_info(pkg, version):
    if version and len(version) > 0:
        ipkg = f"{pkg}=={version}"
    else:
        ipkg = pkg
    return ipkg
