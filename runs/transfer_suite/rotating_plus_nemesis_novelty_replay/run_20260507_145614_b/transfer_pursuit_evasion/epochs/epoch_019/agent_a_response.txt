def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        try:
            obst.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def moves_from(x, y):
        ms = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if ok(nx, ny):
                    ms.append((dx, dy))
        return ms if ms else [(0, 0)]

    self_role = (observation.get("self_role") or "").lower()
    self_evader = ("evader" in self_role) or ("escape" in self_role)
    if not self_evader and "pursuer" in self_role:
        self_evader = False
    opp_evader = not self_evader

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def greedy_step(px, py, tx, ty, evader):
        best = None
        best_key = None
        for dx, dy in moves_from(px, py):
            nx, ny = px + dx, py + dy
            d = dist2(nx, ny, tx, ty)
            score = d if evader else -d
            # deterministic tie-break: prefer higher score, then lexicographically by (dx,dy)
            k = (score, dx, dy)
            if best_key is None or k > best_key:
                best_key = k
                best = (dx, dy)
        return best

    my_moves = moves_from(sx, sy)
    best_move = (0, 0)
    best_val = None
    for dx, dy in my_moves:
        nsx, nsy = sx + dx, sy + dy
        podx, pody = greedy_step(ox, oy, nsx, nsy, opp_evader)
        nosx, nosy = nsx, nsy
        noox, nooy = ox + podx, oy + pody
        d_after = dist2(nosx, nosy, noox, nooy)
        # maximize evader distance, minimize pursuer distance; strong preference to immediate capture/avoid
        if self_evader:
            val = (d_after, -abs(dx) - abs(dy), dx, dy)
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)
        else:
            val = (-d_after, -abs(dx) - abs(dy), -dx, -dy)
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]