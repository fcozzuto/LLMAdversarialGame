def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    opp_reach_bias = 6  # penalize resources opponent is closer to
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        # Evaluate move by best achievable "advantage" to any resource this turn
        move_score = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer resources we can reach sooner; otherwise heavily deprioritize
            beat = 1 if sd < od else (0 if sd == od else -1)
            # Also discourage moving near opponent while "not beating" resources
            near_opp = man(nx, ny, ox, oy)
            score = (beat * 1000 - opp_reach_bias * (od - sd) - 3 * sd - 2 * max(0, 4 - near_opp))
            if move_score is None or score > move_score:
                move_score = score
        # Tie-break deterministically: prefer smaller sd to the best resource, then lexicographic move
        if best is None:
            best = (move_score, dx, dy)
        else:
            if move_score > best[0]:
                best = (move_score, dx, dy)
            elif move_score == best[0]:
                # deterministic secondary: minimize distance to nearest resource from new position
                nd = min(man(nx, ny, rx, ry) for rx, ry in resources)
                bd = min(man(sx + best[1], sy + best[2], rx, ry) for rx, ry in resources)
                if nd < bd or (nd == bd and (dx, dy) < (best[1], best[2])):
                    best = (move_score, dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]