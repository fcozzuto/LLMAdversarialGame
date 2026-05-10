def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []) if len(p) == 2)
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []) if len(p) == 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if len(p) == 2)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if len(p) == 2)
    opp_pos = observation.get("opponent_position", None)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def edge_dist(cx, cy):
        return min(cx, w - 1 - cx, cy, h - 1 - cy)

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def nearest_opp_dist(nx, ny):
        if not oppT and not opp_pos:
            return 99
        best = 99
        if opp_pos and isinstance(opp_pos, (list, tuple)) and len(opp_pos) == 2:
            best = min(best, man((nx, ny), (opp_pos[0], opp_pos[1])))
        for ox, oy in oppT:
            d = abs(nx - ox) + abs(ny - oy)
            if d < best:
                best = d
                if best <= 1:
                    break
        return best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0.0
        cell = (nx, ny)
        if cell in oppT:
            score += 16.0  # flipping opponent is highest priority
        if cell in unclaimed:
            score += 7.0
        if cell in selfT:
            score += 1.0
        if (dx, dy) == (0, 0):
            score -= 1.0

        # Prefer disrupting opponent access: move to reduce distance to opponent territory
        d_opp = nearest_opp_dist(nx, ny)
        score += (8.0 - min(8.0, d_opp * 1.2))

        # Prefer safer expansion away from center-edge contention: slightly prefer outer ring unless contest is close
        cd = edge_dist(nx, ny)
        score += (3.0 - cd) * 0.25

        # Slightly prefer moving closer to our nearest border exit (from current location)
        curr_cd = edge_dist(sx, sy)
        score += (curr_cd - cd) * 0.15

        # Deterministic tie-break: lexicographic by dx,dy
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]