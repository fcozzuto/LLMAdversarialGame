def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = set(map(tuple, observation.get("resources") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manhattan(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    if unclaimed:
        targets = list(unclaimed)
    elif resources:
        targets = list(resources)
    else:
        targets = list(opp_terr) if opp_terr else [(w - 1, h - 1)]

    best_t = targets[0]
    best_d = 10**9
    for tx, ty in targets[:48]:
        d = manhattan(sx, sy, tx, ty)
        if d < best_d:
            best_d = d
            best_t = (tx, ty)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0

        val = 0
        if (nx, ny) in unclaimed:
            val += 7
        if (nx, ny) in opp_terr:
            val += 6
        if (nx, ny) in self_terr:
            val += 1
        if (nx, ny) == (sx, sy):
            val -= 1

        # Prefer moving toward target; if already in opponent territory, keep pressure.
        d = manhattan(nx, ny, best_t[0], best_t[1])
        val += -d

        # Extra: nudge toward border cells adjacent to unclaimed/opp for faster expansion.
        if (nx, ny) != (sx, sy):
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    px, py = nx + ax, ny + ay
                    if inb(px, py) and ((px, py) in unclaimed or (px, py) in opp_terr):
                        val += 0.6
                    if inb(px, py) and (px, py) in obstacles:
                        val -= 0.1

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]