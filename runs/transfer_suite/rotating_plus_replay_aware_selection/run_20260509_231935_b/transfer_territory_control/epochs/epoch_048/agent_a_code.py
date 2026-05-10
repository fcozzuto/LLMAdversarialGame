def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = list(observation.get("unclaimed_cells") or [])
    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    t = int(observation.get("turn_index", 0))
    dirs = dirs[t % 9:] + dirs[:t % 9]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    cx, cy = (w - 1) // 2, (h - 1) // 2
    if unclaimed:
        center = sorted(unclaimed, key=lambda p: (abs(p[0] - cx) + abs(p[1] - cy), p[0], p[1]))
        unclaimed = center[:min(18, len(center))]
    else:
        unclaimed = []

    def best_target(cells):
        if not cells:
            return None
        return min(cells, key=lambda p: (man(sx, sy, p[0], p[1]) - man(ox, oy, p[0], p[1]),
                                           man(sx, sy, p[0], p[1]), p[0], p[1]))

    target = best_target(unclaimed)
    if target is None:
        target = best_target(list(opp_terr)) or (sx, sy)

    ox, oy = int(ox), int(oy)
    best = (0, 0, -10**9)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in self_terr:
            base = 1
        elif (nx, ny) in opp_terr:
            base = 4
        else:
            base = 5  # unclaimed or otherwise
        dt = man(nx, ny, target[0], target[1])
        do = man(ox, oy, nx, ny)
        score = base * 10 - dt * 3 + (2 - do * 0.01)
        if score > best[2]:
            best = (dx, dy, score)

    return [int(best[0]), int(best[1])]