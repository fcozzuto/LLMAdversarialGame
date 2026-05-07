def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def kdist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_val = -10**18
    # Tie-break determinism: sort by (x,y) when values match
    res_sorted = sorted(resources)
    for rx, ry in res_sorted:
        sd = kdist(sx, sy, rx, ry)
        od = kdist(ox, oy, rx, ry)
        if sd == 0:
            return [0, 0]
        # Primary: win the race (arrive no later); secondary: prefer farther opponent disadvantage.
        race = (od - sd)
        # Innovation: opponent archetype sweep_rows -> reward targets aligned with opponent in x or y
        align = 0
        if rx == ox or ry == oy:
            align = 2
        # Small penalty to reduce dithering
        val = race * 100 + align * 10 - sd
        if val > best_val:
            best_val = val
            best = (rx, ry)

    rx, ry = best
    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)
    return [dx, dy]