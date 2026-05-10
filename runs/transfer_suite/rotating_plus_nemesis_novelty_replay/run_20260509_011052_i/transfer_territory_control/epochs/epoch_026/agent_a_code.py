def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        return set((int(p[0]), int(p[1])) for p in (observation.get(key, []) or []) if p is not None and len(p) >= 2)

    obstacles = to_set("obstacles")
    self_terr = to_set("self_territory")
    opp_terr = to_set("opponent_territory")
    unclaimed = to_set("unclaimed_cells")

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def man(a, b, x, y):
        return abs(a - x) + abs(b - y)

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        score = -man(ox, oy, nx, ny)
        if (nx, ny) in unclaimed:
            score += 8
        if (nx, ny) in self_terr:
            score += 3
        if (nx, ny) in opp_terr:
            score -= 4
        if score > best_score:
            best_score = score
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best