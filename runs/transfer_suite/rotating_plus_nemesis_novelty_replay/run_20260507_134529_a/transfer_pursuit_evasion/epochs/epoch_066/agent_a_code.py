def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx); dy = abs(ay - by)
        return dx if dx > dy else dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # Corner "intent" estimate: evader tends toward their nearest corner; pursuer should preempt it.
    opp_corner = min(corners, key=lambda c: cheb(ox, oy, c[0], c[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = None

    # Greedy 2-ply lookahead on our position only (opponent assumed to chase/evade deterministically by role).
    # For tie-breaking determinism, use a fixed priority order among moves.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        if is_evader:
            # Evade: maximize distance to pursuer and drift to farthest corner from pursuer.
            far_corner = max(corners, key=lambda c: cheb(ox, oy, c[0], c[1]))
            dist1 = cheb(nx, ny, ox, oy)
            drift = cheb(nx, ny, far_corner[0], far_corner[1])
            # discourage edging into obstacles vicinity (soft penalty)
            adj_obs = 0
            for ex, ey in obs:
                if abs(ex - nx) <= 1 and abs(ey - ny) <= 1:
                    adj_obs += 1
            score = -(dist1 * 10 + drift - adj_obs * 2)  # minimize negative => maximize
        else:
            # Pursue: reduce distance to opponent while also minimizing distance to opponent's likely corner.
            dist1 = cheb(nx, ny, ox, oy)
            preempt = cheb(nx, ny, opp_corner[0], opp_corner[1])
            adj_obs = 0
            for ex, ey in obs:
                if abs(ex - nx) <= 1 and abs(ey - ny) <= 1:
                    adj_obs += 1
            score = dist1 * 10 + preempt - 0.5 * cheb(ox, oy, opp_corner[0], opp_corner[1]) + adj_obs * 3

        if best_score is None or score < best_score if not is_evader else score < best_score:
            best_score = score
            best_move = [dx, dy]

    # If somehow no move valid (shouldn't happen), stay.
    return [int(best_move[0]), int(best_move[1])]