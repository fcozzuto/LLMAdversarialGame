def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    evader = ("evad" in self_role) or ("run" in self_role) or ("escape" in self_role) or ("hare" in self_role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # deterministic tie-break: prefer axis moves over diagonals, then avoid staying
    order = [(0, -1), (-1, 0), (1, 0), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    move_list = [m for m in order if m in moves] + [m for m in moves if m not in order]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best = None  # (score, nx, ny)
    for dx, dy in move_list:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        # pursuer: minimize distance; evader: maximize distance
        # slight bias to move away/towards center depending on role
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_bias = cheb(int(nx), int(ny), int(cx), int(cy))
        if evader:
            score = (-d * 10 - center_bias)  # maximize d, then maximize center_bias via negative
        else:
            score = (d * 10 + center_bias)   # minimize d, then minimize center_bias
        if best is None or score < best[0]:
            best = (score, nx, ny)

    if best is None:
        return [0, 0]
    _, nx, ny = best
    return [nx - sx, ny - sy]