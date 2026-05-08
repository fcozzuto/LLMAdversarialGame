def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def pos(v, default=(0, 0)):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return (int(v[0]), int(v[1]))
        if isinstance(v, dict):
            p = v.get("position", v.get("pos", None))
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                return (int(p[0]), int(p[1]))
        return default

    sx, sy = pos(observation.get("self_position", None), (0, 0))
    ox, oy = pos(observation.get("opponent_position", None), (sx, sy))

    obs = set()
    for o in observation.get("obstacles", []) or []:
        x, y = pos(o, None) if o is not None else (None, None)
        if x is None:
            continue
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    def is_free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    resources = []
    for r in observation.get("resources", []) or []:
        x, y = pos(r, None) if r is not None else (None, None)
        if x is None:
            continue
        if is_free(x, y):
            resources.append((x, y))

    if resources:
        tx, ty = min(resources, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
    else:
        tx, ty = ox, oy

    best = (10**9, 0, 0, 0)  # (dist, attack_bonus, dx, dy)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if not is_free(nx, ny):
                continue
            dist = abs(nx - tx) + abs(ny - ty)
            attack = 0
            if (nx, ny) == (ox, oy):
                attack = -1000
            if dist + attack < best[0]:
                best = (dist + attack, attack, dx, dy)

    if best[0] < 10**9:
        return [best[2], best[3]]

    # Fallback: try any free adjacent move, else stay.
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if dx == 0 and dy == 0:
                continue
            if is_free(nx, ny):
                return [dx, dy]
    return [0, 0]