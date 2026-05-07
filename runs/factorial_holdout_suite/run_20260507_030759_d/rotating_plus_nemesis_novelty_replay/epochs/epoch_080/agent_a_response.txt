def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best_target = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources where we can arrive earlier than opponent (race win),
        # and where our and opponent reach have different axes (harder for sweep).
        axis_diff = abs(ry - oy) + abs(rx - ox)
        col_pref = abs(rx - (w - 1 if sy < h // 2 else 0))  # steer away from opponent sweep lane
        arrive_margin = do - ds
        # Deterministic lexicographic preference
        key = (-(arrive_margin * 1000 + axis_diff * 10 - ds), -(col_pref * 3), ds, abs(rx - sx) + abs(ry - sy))
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        nds = cheb(nx, ny, tx, ty)
        ndo = cheb(ox, oy, tx, ty)
        # Evaluate immediate progress and keep moving in race-positive direction
        score = (nds * 1000 - (ndo - nds) * 50) + (abs(nx - sx) + abs(ny - sy)) * 0.01
        # Deterministic tie-break: prefer larger dx towards target x, then larger dy towards target y
        tieb = (-(nx - tx) * (sx - tx >= 0) - (ny - ty) * (sy - ty >= 0), -dx, -dy)
        cur = (score, tieb)
        if best_score is None or cur < best_score:
            best_score = cur
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]