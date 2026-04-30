def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    opp_stay = True if len(resources) == 0 else False

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        if resources:
            # Prefer resources where we are at least as close as the opponent, else block by reducing gap.
            val = 0
            for (rx, ry) in resources:
                d_me = cheb(nx, ny, rx, ry)
                d_op = cheb(ox, oy, rx, ry)
                # If we can reach no slower than opponent, strongly favor; if not, mildly discourage.
                if d_me <= d_op:
                    val += 120 - 10 * d_me
                else:
                    # Increase value if we reduce opponent advantage by moving closer to that resource.
                    val += (d_op - d_me) * 6
                # Small anti-stalemate: prefer not moving too far from opponent when we are winning local races.
                val += -2 * cheb(nx, ny, ox, oy)
            # Additional deterministic tie-break: favor moves that increase distance from opponent (risk-off) when no local win.
            # Estimate local win by comparing our current race advantage across all resources quickly.
            quick_adv = -10**9
            for (rx, ry) in resources[:min(6, len(resources))]:
                adv = cheb(nx, ny, rx, ry) - cheb(ox, oy, rx, ry)
                if adv > quick_adv:
                    quick_adv = adv
            if quick_adv > 0:
                val += 10 * cheb(nx, ny, ox, oy)
        else:
            # No visible resources: maximize distance from opponent while staying legal.
            val = 1000 * cheb(nx, ny, ox, oy) - 2 * cheb(nx, ny, (w - 1), (h - 1))

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]