def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        out = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx0, cy0 = sx, sy

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    curd = man(cx0, cy0, ox, oy)
    best_move = (0, 0)
    best = -10**18

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in unclaimed:
            score += 7
        if (nx, ny) in self_terr:
            score += 2
        if (nx, ny) in opp_terr:
            score -= 6

        nd = man(nx, ny, ox, oy)
        score += (curd - nd) * 3  # prefer increasing distance from opponent
        # keep a mild preference for staying in bounds/near center
        score -= (abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)) * 0.05

        if score > best:
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]