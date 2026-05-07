def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    if w <= 0 or h <= 0:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = bx - ax
        dy = by - ay
        axd = -dx if dx < 0 else dx
        ayd = -dy if dy < 0 else dy
        return axd if axd > ayd else ayd

    best_move = (0, 0)
    best_val = -10**18

    # Deterministic move selection: maximize immediate "take-advantage"
    # where advantage = opponent distance - our distance, plus strong on-resource bonus.
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not inb(nx, ny):
            continue

        val = 0
        on_res = 0
        if resources:
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                d_own = cheb(nx, ny, rx, ry)
                d_opp = cheb(ox, oy, rx, ry)
                adv = d_opp - d_own
                # Strongly prefer stepping onto a resource
                if d_own == 0:
                    on_res += 1
                    val += 200000 + adv * 10
                else:
                    # Prefer moves that reduce our distance and/or increase opponent distance disadvantage
                    val += adv * 10 - d_own
            # If multiple resources overlap, stepping on one is already handled; still reward closeness to any remaining.
            val += -1 * (abs(nx - sx) + abs(ny - sy))
        else:
            # No visible resources: drift toward center-ish while avoiding obstacles
            cx = (w - 1) // 2
            cy = (h - 1) // 2
            val = -cheb(nx, ny, cx, cy)

        # Tie-breaker: also reduce opponent's ability by moving away when on equal advantage
        opp_escape = cheb(nx, ny, ox, oy)
        val += opp_escape * 0.01

        if val > best_val:
            best_val = val
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]