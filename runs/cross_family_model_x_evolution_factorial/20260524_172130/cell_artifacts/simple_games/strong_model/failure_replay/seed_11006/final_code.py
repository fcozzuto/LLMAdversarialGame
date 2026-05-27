def choose_move(observation):
    g = observation if isinstance(observation, dict) else {}
    def i(v, d=0):
        try:
            return int(v)
        except:
            try:
                return int(float(v))
            except:
                return d
    def p(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return (i(v[0]), i(v[1]))
        if isinstance(v, dict):
            x = v.get("x", v.get("col", v.get("c")))
            y = v.get("y", v.get("row", v.get("r")))
            if x is not None and y is not None:
                return (i(x), i(y))
        return None
    def L(v):
        return v if isinstance(v, (list, tuple)) else ([] if v is None else [v])
    w = i(g.get("grid_width", g.get("width", 0)))
    h = i(g.get("grid_height", g.get("height", 0)))
    s = p(g.get("self_position", g.get("position"))) or p(g.get("my_position"))
    if s is None:
        return [0, 0]
    e = p(g.get("opponent_position", g.get("enemy_position"))) or p(g.get("opponent"))
    blocks = set()
    for k in ("obstacles", "walls", "blocked", "self_path", "opponent_path"):
        for v in L(g.get(k)):
            q = p(v)
            if q is not None:
                blocks.add(q)
    foods = []
    for v in L(g.get("resources", g.get("resource_positions"))):
        q = p(v)
        if q is not None:
            foods.append(q)
    ms = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    best = None
    for dx, dy in ms:
        nx, ny = s[0] + dx, s[1] + dy
        if nx < 0 or ny < 0 or (w and nx >= w) or (h and ny >= h) or (nx, ny) in blocks:
            continue
        score = 0
        if e is not None:
            d0 = abs(s[0] - e[0]) + abs(s[1] - e[1])
            d1 = abs(nx - e[0]) + abs(ny - e[1])
            score += (d0 - d1) * 3
        if foods:
            score += max(0, 20 - min(abs(nx - x) + abs(ny - y) for x, y in foods))
        score += [0, 1, 0, 1][(dx, dy) != (0, 1)]
        if best is None or score > best[0]:
            best = (score, dx, dy)
    if best is not None:
        return [best[1], best[2]]
    return [0, 0]
