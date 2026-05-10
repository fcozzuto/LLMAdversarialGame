def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x, y, u, v):
        dx, dy = x - u, y - v
        return dx * dx + dy * dy

    legal_self = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            legal_self.append((dx, dy, nx, ny))

    if not legal_self:
        return [0, 0]

    best_move = [0, 0]
    best_val = 10**18

    # Minimax: assume opponent will move to maximize our distance after our move
    for dx, dy, nsx, nsy in legal_self:
        if nsx == ox and nsy == oy:
            return [dx, dy]

        legal_opp = []
        for odx, ody in dirs:
            nox, noy = ox + odx, oy + ody
            if inb(nox, noy):
                legal_opp.append((nox, noy))
        if not legal_opp:
            legal_opp = [(ox, oy)]

        worst = -1
        for nox, noy in legal_opp:
            v = dist2(nsx, nsy, nox, noy)
            if v > worst:
                worst = v

        # Tie-break: prefer moves that also reduce immediate distance
        immediate = dist2(nsx, nsy, ox, oy)
        key = (worst, immediate)
        best_key = (best_val, dist2(sx + best_move[0], sy + best_move[1], ox, oy))
        if key < best_key:
            best_val = worst
            best_move = [dx, dy]

    return best_move