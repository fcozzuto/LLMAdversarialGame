def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y): return 0 <= x < W and 0 <= y < H

    def to_set(lst):
        s = set()
        if not lst:
            return s
        for p in lst:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if inb(x, y):
                    s.add((x, y))
        return s

    obstacles = to_set(observation.get("obstacles"))
    unclaimed = to_set(observation.get("unclaimed_cells"))
    opp_t = to_set(observation.get("opponent_territory"))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    opp_neighbors = []
    for (x, y) in opp_t:
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in unclaimed:
                opp_neighbors.append((nx, ny))
    if opp_neighbors:
        targets = opp_neighbors
    elif unclaimed:
        targets = list(unclaimed)
    else:
        targets = [(ox, oy)]

    def best_step():
        best_move = (0, 0)
        best_val = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            # Prefer capturing/attacking boundary; otherwise expand toward nearest target.
            val = 0
            if (nx, ny) in opp_t:
                val += 2000
            if (nx, ny) in unclaimed:
                val += 500
            # Encourage moving toward the chosen frontier/targets.
            d = min(man(nx, ny, tx, ty) for (tx, ty) in targets)
            val -= 3 * d
            # Slightly bias away from opponent when not attacking.
            val -= 0.5 * man(nx, ny, ox, oy)
            # Deterministic tie-break: smaller dx, then smaller dy after value.
            if val > best_val or (val == best_val and (dx, dy) < best_move):
                best_val = val
                best_move = (dx, dy)
        return best_move

    dx, dy = best_step()
    return [int(dx), int(dy)]