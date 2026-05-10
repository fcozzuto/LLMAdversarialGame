def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = {tuple(p) for p in (observation.get("obstacles") or [])}
    self_set = {tuple(p) for p in (observation.get("self_territory") or [])}
    opp_set = {tuple(p) for p in (observation.get("opponent_territory") or [])}
    un_set = {tuple(p) for p in (observation.get("unclaimed_cells") or [])}

    def centroid(cset, fallback):
        if not cset:
            return fallback
        sxm = sum(x for x, _ in cset) / len(cset)
        sym = sum(y for _, y in cset) / len(cset)
        return sxm, sym

    my_cx, my_cy = centroid(self_set, ((w - 1) / 4.0, (h - 1) / 4.0))
    op_cx, op_cy = centroid(opp_set, ((3 * (w - 1)) / 4.0, (3 * (h - 1)) / 4.0))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    def neighbors8(x, y):
        out = []
        for dx, dy in dirs:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                out.append((nx, ny))
        return out

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        val = 0.0

        if (nx, ny) in opp_set:
            adj_self = sum((tx, ty) in self_set for (tx, ty) in neighbors8(nx, ny))
            val += 120.0 + 8.0 * adj_self
        elif (nx, ny) in un_set:
            adj_self = sum((tx, ty) in self_set for (tx, ty) in neighbors8(nx, ny))
            adj_opp = sum((tx, ty) in opp_set for (tx, ty) in neighbors8(nx, ny))
            dist_to_opp = abs(nx - op_cx) + abs(ny - op_cy)
            val += 40.0 + 10.0 * adj_self
            val += 2.0 * (8 - adj_opp)  # avoid handing easy counterclaim lanes
            val += 8.0 / (1.0 + dist_to_opp)  # pressure toward opponent
        elif (nx, ny) in self_set:
            val += 4.0
        else:
            val += -5.0

        # Prefer moves that extend outward from our territory center (not just wander)
        val += 3.0 * ((abs(nx - my_cx) + abs(ny - my_cy)) - (abs(sx - my_cx) + abs(sy - my_cy)))

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]