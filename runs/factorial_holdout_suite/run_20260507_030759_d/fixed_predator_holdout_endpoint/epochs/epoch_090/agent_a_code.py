def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev steps with 8-neighborhood

    best = None
    best_is_deny = False
    best_sd = None
    best_od = None

    for rx, ry in resources:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        is_deny = sd <= od
        if best is None:
            best = (rx, ry)
            best_is_deny, best_sd, best_od = is_deny, sd, od
        else:
            if is_deny != best_is_deny:
                if is_deny:
                    best, best_is_deny, best_sd, best_od = (rx, ry), True, sd, od
            elif is_deny:
                if sd < best_sd or (sd == best_sd and od < best_od):
                    best, best_sd, best_od = (rx, ry), sd, od
            else:
                # contestable fallback: maximize opponent disadvantage; tie by smaller self distance
                cur_score = od - sd
                best_score = best_od - best_sd
                if cur_score > best_score or (cur_score == best_score and sd < best_sd):
                    best, best_sd, best_od = (rx, ry), sd, od

    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nd = dist(nx, ny, tx, ty)

        # slight anti-opponent: prefer moves that increase our lead on target vs opponent
        my_next = nd
        opp_next = dist(ox, oy, tx, ty)
        lead = opp_next - my_next

        # deterministic tie-breaker prefers not to increase distance first, then lexicographic dx,dy
        val = (-(lead), nd, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]