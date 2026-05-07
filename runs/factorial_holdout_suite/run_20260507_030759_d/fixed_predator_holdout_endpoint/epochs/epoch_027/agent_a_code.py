def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def sqd(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    best_move = [0, 0]
    best_score = None
    # One-step lookahead: choose move that maximizes potential to collect resources first.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        nx = clamp(nx, 0, w - 1)
        ny = clamp(ny, 0, h - 1)
        if (nx, ny) in obstacles:
            continue
        move_score = -10**18
        # If landing on a resource, prioritize immediately.
        on_res = (nx, ny) in set(map(tuple, resources))
        if on_res:
            move_score = 10**12
        else:
            # Evaluate best resource after this move.
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                self_d = sqd(nx, ny, rx, ry)
                opp_d = sqd(ox, oy, rx, ry)
                # Prefer resources where we are relatively closer; penalize being far.
                val = (opp_d - self_d) * 1000 - self_d
                # Small obstacle proximity nudge for the moved-to cell.
                px = abs(nx - rx) + abs(ny - ry)
                if px == 0:
                    val += 10**9
                # If opponent is already closer, discourage.
                if opp_d < self_d:
                    val -= 5000
                if val > move_score:
                    move_score = val
        # Deterministic tiebreak: prefer moves that reduce Chebyshev distance to best resource direction,
        # then lexicographic by (dx,dy).
        if best_score is None or move_score > best_score:
            best_score = move_score
            best_move = [dx, dy]
        elif move_score == best_score:
            # tie-break deterministically using direction to current "best" resource by same heuristic
            # (computed only for tie-breaking simplicity).
            tx_best, ty_best = resources[0]
            cur0 = resources[0]
            for rx, ry in resources:
                s = sqd(sx, sy, rx, ry)
                o = sqd(ox, oy, rx, ry)
                if (o - s, -s) > (sqd(sx, sy, cur0[0], cur0[1]) * 0 + (sqd(ox, oy, cur0[0], cur0[1]) - sqd(sx, sy, cur0[0], cur0[1])), 0):
                    cur0 = (rx, ry)
            tx_best, ty_best = cur0
            curd_best = max(abs(tx_best - sx), abs(ty_best - sy))
            nd_best = max(abs(tx_best - (sx + dx)), abs(ty_best - (sy + dy)))
            best_nd = max(abs(tx_best - (sx + best_move[0])), abs(ty_best - (sy + best_move[1])))
            if nd_best < best_nd or (nd_best == best_nd and (dx, dy) > (best_move[0], best_move[1])):
                best_move = [dx, dy]
    return best_move