def choose_move(observation):
    W = observation["grid_width"]; H = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    res = []
    seen = set()
    for p in resources:
        if p and len(p) >= 2:
            t = (p[0], p[1])
            if t not in obs and t not in seen:
                seen.add(t); res.append(t)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < W and 0 <= y < H
    def legal(x, y): return inb(x, y) and (x, y) not in obs
    def md(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx + dy
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    best_move = (0, 0)
    best_val = -10**18

    center_x = (W - 1) // 2
    center_y = (H - 1) // 2

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        if res:
            my_d = 10**9
            target = None
            for r in res:
                d = md(nx, ny, r[0], r[1])
                if d < my_d:
                    my_d = d; target = r
            # Denial: prefer resources where opponent is farther than me after this move
            opp_d = md(ox, oy, target[0], target[1])
            val = (opp_d - my_d) * 120 - my_d * 3
            # Strong capture bonus, but only if it also denies opponent
            if (nx, ny) == (target[0], target[1]):
                val += 100000
                val += (opp_d - 1) * 50
            # Mild preference to reduce overall closeness to opponent
            val += cheb(ox, oy, nx, ny) * 2
        else:
            # No resources: head toward center while keeping distance from opponent
            val = -cheb(nx, ny, center_x, center_y) * 8 + cheb(nx, ny, ox, oy) * 6

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]