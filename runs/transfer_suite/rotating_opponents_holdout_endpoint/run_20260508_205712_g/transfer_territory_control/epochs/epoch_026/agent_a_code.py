def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((int(x), int(y)) for x, y in obstacles_list)

    unclaimed_list = observation.get("unclaimed_cells", []) or []
    resources_list = observation.get("resources", []) or []
    opp_terr_list = observation.get("opponent_territory", []) or []
    unclaimed = set((int(x), int(y)) for x, y in unclaimed_list)
    resources = set((int(x), int(y)) for x, y in resources_list)
    opp_terr = set((int(x), int(y)) for x, y in opp_terr_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_dx, best_dy, best_score = 0, 0, -10**18

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_self = abs(nx - sx) + abs(ny - sy)
        d_opp = abs(nx - ox) + abs(ny - oy)

        # Prefer unclaimed/resources; avoid being too close to opponent; mildly prefer expanding into opponent territory
        score = 0
        if (nx, ny) in unclaimed:
            score += 200
        if (nx, ny) in resources:
            score += 120
        if (nx, ny) in opp_terr:
            score += 60

        # Encourage moving (less stay), and keep distance from opponent
        score -= 2 * d_self
        score += 0.8 * d_opp

        # Prefer cells closer to center if no strong target
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_dist = abs(nx - cx) + abs(ny - cy)
        score -= 0.05 * center_dist

        # Deterministic tie-break: fixed move order already; keep first best
        if score > best_score:
            best_score = score
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]