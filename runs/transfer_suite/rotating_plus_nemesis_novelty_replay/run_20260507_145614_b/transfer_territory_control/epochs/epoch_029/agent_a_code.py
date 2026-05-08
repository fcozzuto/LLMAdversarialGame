def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = {tuple(p) for p in (observation.get("obstacles") or []) if p and len(p) >= 2}
    self_t = {tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) >= 2}
    opp_t = {tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2}
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = (0, 0)
    bestv = -10**18

    def edge_dist(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        dcenter = abs(nx - cx) + abs(ny - cy)
        dopp = abs(nx - ox) + abs(ny - oy)

        if (nx, ny) in opp_t:
            v = 1000 - 6 * dcenter - 1.2 * dopp + 2.0 / (1 + edge_dist(nx, ny))
        elif (nx, ny) in self_t:
            v = 120 - 2.0 * dcenter + 0.5 / (1 + edge_dist(nx, ny))
        else:
            if unclaimed:
                # nearest unclaimed distance as a proxy for expansion
                dmin = min(abs(nx - ux) + abs(ny - uy) for ux, uy in unclaimed[:min(12, len(unclaimed))])
                v = 200 - 3.5 * dcenter - 2.0 * dmin - 0.6 * dopp + 1.5 / (1 + edge_dist(nx, ny))
            else:
                v = 50 - 2.0 * dcenter + 0.1 * dopp

        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]