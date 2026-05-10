def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", []) or []))
    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Prefer edge/corners against a center-claiming opponent, while stealing nearby opponent cells.
    def edge_score(x, y):
        return -min(x, w - 1 - x, y, h - 1 - y)

    best = None
    best_move = [0, 0]

    opp_list = list(opp_terr)
    # Simple nearest-opponent proxy (no full search): use Manhattan distance with capped scan.
    def nearest_opp_dist(x, y):
        if not opp_list:
            return 999
        md = 999
        lim = 18 if len(opp_list) > 18 else len(opp_list)
        # deterministic sampling: first lim elements
        for i in range(lim):
            ox, oy = opp_list[i]
            d = abs(ox - x) + abs(oy - y)
            if d < md:
                md = d
                if md == 0:
                    break
        return md

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            val = -10**9
        else:
            val = 0
            if (nx, ny) in unclaimed:
                val += 60
            if (nx, ny) in opp_terr:
                # flipping on entry is enabled; steal control.
                val += 80
            if (nx, ny) in self_terr:
                val -= 5
            val += edge_score(nx, ny) * 6
            # Nudge toward opponent perimeter, but still favor edges.
            d = nearest_opp_dist(nx, ny)
            val += (12 - min(12, d)) * 2
            # Small preference to move (avoid getting stuck).
            val -= (0 if (dx == 0 and dy == 0) else 0)
        if best is None or val > best:
            best = val
            best_move = [dx, dy]
    return best_move