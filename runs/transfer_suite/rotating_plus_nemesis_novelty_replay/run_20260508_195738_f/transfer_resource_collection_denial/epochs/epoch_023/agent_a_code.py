def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((int(p[0]), int(p[1])) for p in obstacles_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        # Drift toward farthest corner from opponent (denial-ish) deterministically
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: man(ox, oy, c[0], c[1]) - 0.1 * man(sx, sy, c[0], c[1]))
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [int(dx), int(dy)]

    res = [(int(r[0]), int(r[1])) for r in resources]

    def best_for(posx, posy):
        best = None
        for rx, ry in res:
            sd = man(posx, posy, rx, ry)
            od = man(ox, oy, rx, ry)
            # resource_denier: prefer states where opponent is relatively far and we're relatively close
            score = (od - sd) * 10 - sd
            if best is None or score > best[0] or (score == best[0] and sd < best[1]):
                best = (score, sd)
        return best[0] if best else -10**9

    best_move = [0, 0]
    best_val = -10**18
    # Small tie-break: prefer moves that reduce our distance to the currently best resource
    base = best_for(sx, sy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        val = best_for(nx, ny)
        if val > best_val or (val == best_val and (man(nx, ny, ox, oy) < man(sx, sy, ox, oy) or base == val)):
            best_val = val
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]