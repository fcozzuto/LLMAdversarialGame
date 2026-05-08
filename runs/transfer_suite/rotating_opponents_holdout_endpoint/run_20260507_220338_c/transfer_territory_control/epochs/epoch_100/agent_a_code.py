def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < int(w) and 0 <= y < int(h):
                obstacles.add((x, y))

    def inside(x, y):
        return 0 <= x < int(w) and 0 <= y < int(h)

    dirs = [(0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)]
    man = lambda ax, ay, bx, by: (ax - bx if ax >= bx else bx - ax) + (ay - by if ay >= by else by - ay)

    resources = observation.get("resources") or []
    rcoords = []
    for r in resources:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inside(x, y) and (x, y) not in obstacles:
                rcoords.append((x, y))

    opp_adj = man(sx, sy, ox, oy) == 1

    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        if opp_adj and man(nx, ny, ox, oy) == 0:
            continue

        val = 0
        if rcoords:
            d = min(man(nx, ny, rx, ry) for rx, ry in rcoords)
            val += 1000 - d
            if dx == 0 and dy == 0:
                val -= 5
        else:
            # No known resources: prefer moving away from opponent if adjacent, else closer.
            d_to_opp = man(nx, ny, ox, oy)
            if opp_adj:
                val += d_to_opp
            else:
                val += -d_to_opp

        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]