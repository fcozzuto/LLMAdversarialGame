def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or observation.get("unclaimed") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_val = -10**18
    best = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) == (ox, oy):
            continue

        dist_to_opp = manh(nx, ny, ox, oy)
        val = 0

        if (nx, ny) in selfT:
            val += 12
        if (nx, ny) in oppT:
            val += 160 + dist_to_opp  # flipping into opponent territory is strong

        if (nx, ny) in unclaimed:
            val += 220

        if unclaimed:
            # Encourage expansion toward nearest unclaimed while staying away from opponent
            dmin = 10**9
            for ux, uy in unclaimed:
                d = manh(nx, ny, ux, uy)
                if d < dmin:
                    dmin = d
            val += max(-240, 260 - 18 * dmin)

        # Control stability: slightly prefer moves that increase distance from opponent early
        val += 4 * dist_to_opp

        # Deterministic tie-breaker: fixed direction priority already ensures consistency
        if val > best_val:
            best_val = val
            best = [dx, dy]

    return best