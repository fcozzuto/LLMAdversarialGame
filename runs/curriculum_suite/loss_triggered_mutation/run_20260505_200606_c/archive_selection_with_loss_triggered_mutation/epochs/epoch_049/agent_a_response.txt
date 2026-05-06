def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_move = (0, 0)

    if not resources:
        # fallback: move to increase distance from opponent while avoiding obstacles
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles: 
                continue
            key = (md(nx, ny, ox, oy), nx, ny)
            if best is None or key > best:
                best = key
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Deny: choose the resource where opponent is currently closest relative to us,
        # but estimate after our step by using our distance from next position.
        best_adv = None
        best_res = None
        for rx, ry in resources:
            od = md(ox, oy, rx, ry)
            nd = md(nx, ny, rx, ry)
            adv = od - nd  # higher means we are closer than opponent
            # prioritize making the opponent's best target contested and improve after our move
            key = (adv, -nd, -rx, -ry)
            if best_adv is None or key > best_adv:
                best_adv = key
                best_res = (rx, ry)
        rx, ry = best_res
        # Also prefer moving toward the selected contested resource and slightly away from opponent
        our_d = md(nx, ny, rx, ry)
        opp_d = md(nx, ny, ox, oy)
        key = (best_adv[0], -our_d, opp_d, -dx, -dy, nx, ny)
        if best is None or key > best:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]