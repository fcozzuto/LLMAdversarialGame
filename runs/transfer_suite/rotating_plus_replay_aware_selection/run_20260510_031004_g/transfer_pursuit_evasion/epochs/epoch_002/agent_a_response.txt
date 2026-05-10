def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_role = observation.get("self_role", "")
    opp_role = observation.get("opponent_role", "")
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles)

    is_pursuer = (self_role.lower() == "pursuer") or (opp_role.lower() == "evader")
    if self_role == "" and opp_role == "":
        is_pursuer = True

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                moves.append((dx, dy))

    if not moves:
        return [0, 0]

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))

    def score(nx, ny):
        d_opp = dist2(nx, ny, ox, oy)
        if is_pursuer:
            # Minimize distance to opponent; tie-break towards moving generally closer to far_corner
            return (d_opp, abs(nx - sx) + abs(ny - sy), nx, ny)
        else:
            # Maximize distance to opponent; also prefer moving toward far_corner
            dc = dist2(nx, ny, far_corner[0], far_corner[1])
            return (-d_opp, -dc, abs(nx - sx) + abs(ny - sy), nx, ny)

    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        k = score(nx, ny)
        if best_key is None or k < best_key:
            best_key = k
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]