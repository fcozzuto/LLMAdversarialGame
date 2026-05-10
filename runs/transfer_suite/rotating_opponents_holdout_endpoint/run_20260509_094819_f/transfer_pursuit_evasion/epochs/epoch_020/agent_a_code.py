def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            blocked.add((int(o[0]), int(o[1])))

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("evasion" in role) or ("escape" in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def exits(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                c += 1
        return c

    # Evader target alternates between far corners deterministically by turn_index.
    ti = int(observation.get("turn_index", 0) or 0)
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    if is_evader:
        tx, ty = corners[ti % 4]
        # If pursuer is closer to that corner than our opposite, swap deterministically.
        d_tc = cheb(ox, oy, tx, ty)
        mx, my = corners[(ti + 2) % 4]
        if cheb(ox, oy, mx, my) > d_tc:
            tx, ty = mx, my
    best = None
    best_sc = -10**18
    for dx, dy in sorted(moves):
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        ex = exits(nx, ny)
        if is_evader:
            # Max distance from pursuer; also prefer moves that keep options.
            # Slightly bias away from the current nearest corner direction.
            dc = cheb(nx, ny, tx, ty)
            sc = (d * 1000) + (ex * 7) + (dc * 2)
            # If already cornering tightly, favor staying mobile more.
            if ex <= 2:
                sc += ex * 20
        else:
            # Pursuer: minimize distance; prefer staying with many future exits.
            sc = (-(d * 1000)) + (ex * 9)
            # Strongly avoid giving the evader maximal separation next.
            far = max(cheb(nx + ddx, ny + ddy, ox, oy) for ddx, ddy in moves if ok(nx + ddx, ny + ddy))
            sc -= far * 2
        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]
    return best if best is not None else [0, 0]