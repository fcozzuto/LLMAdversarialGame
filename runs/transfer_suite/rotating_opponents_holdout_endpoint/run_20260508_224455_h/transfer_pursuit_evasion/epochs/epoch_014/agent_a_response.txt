def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obstacles
    def dist2(x, y):
        dx = x - ox
        dy = y - oy
        return dx * dx + dy * dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    evader_keys = ("evader", "evade", "escape", "runner")
    we_evade = any(k in role for k in evader_keys) and not any(k in opp_role for k in evader_keys)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    def pref_dir(nx, ny):
        # Deterministic bias toward reducing/increasing manhattan to opponent,
        # and, when evading, toward the farthest corner to oppose wall-running.
        md = abs(nx - ox) + abs(ny - oy)
        mc = abs(nx - far_corner[0]) + abs(ny - far_corner[1])
        if we_evade:
            return (md, -mc)  # want larger md, smaller mc tie-break
        return (-md, mc)      # want smaller md, smaller mc tie-break

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        d = dist2(nx, ny)
        if we_evade:
            key = (d, pref_dir(nx, ny))
            better = best_key is None or key > best_key
        else:
            key = (-d, pref_dir(nx, ny))  # maximize -d == minimize d
            better = best_key is None or key > best_key
        if better:
            best_key = key
            best = [dx, dy]

    return best if best is not None else [0, 0]