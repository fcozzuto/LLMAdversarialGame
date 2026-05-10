def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]
    if not resources:
        tx, ty = (0, 0)
        if (sx + ox + sy + oy) % 2 == 0:
            tx, ty = (w - 1, h - 1)
        else:
            tx, ty = (0, h - 1)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]
        if 0 <= nx < w and (nx, sy) not in obstacles:
            return [dx, 0]
        if 0 <= ny < h and (sx, ny) not in obstacles:
            return [0, dy]
        return [0, 0]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    neigh = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                neigh.append((dx, dy))
    neigh.append((0, 0))

    best = None
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        # pick the resource with best "race" advantage from the prospective position
        best_r = None
        best_score = None
        for rx, ry in resources:
            sd = manh(nx, ny, rx, ry)
            od = manh(ox, oy, rx, ry)
            # encourage taking resources we reach strictly sooner; tie-break by closer to resource
            race = od - sd
            # prefer moves that also reduce opponent's next-best advantage (approx via their distance)
            opp_closer = manh(ox, oy, nx, ny) - manh(ox, oy, rx, ry)
            s = (race, -sd, -opp_closer, -rx, -ry)
            if best_score is None or s > best_score:
                best_score = s
                best_r = (rx, ry)
        # secondary goal: if races are equal, prefer moves that increase distance from opponent when resources remain
        if best_r is not None:
            s2 = best_score + (manh(nx, ny, ox, oy),)
        else:
            s2 = (0, 0, 0, 0, manh(nx, ny, ox, oy))
        if best is None or s2 > best:
            best = s2
            best_move = [dx, dy]
    return best_move