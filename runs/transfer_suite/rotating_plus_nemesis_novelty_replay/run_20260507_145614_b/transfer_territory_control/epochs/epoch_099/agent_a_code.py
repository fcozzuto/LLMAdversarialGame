def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    opp = observation.get("opponent_position") or [0, 0]
    ox, oy = int(opp[0]) if opp and len(opp) > 0 and opp[0] is not None else 0, int(opp[1]) if opp and len(opp) > 1 and opp[1] is not None else 0

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.add((x, y))

    recent = set()
    path = observation.get("self_path") or []
    for p in path[-6:]:
        if p and len(p) >= 2:
            recent.add((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        val = -dist * 10
        if (nx, ny) in unclaimed:
            val += 500
        if (nx, ny) in recent:
            val -= 30
        if dx == 0 and dy == 0:
            val -= 5
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]