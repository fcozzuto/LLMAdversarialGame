def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    obstacles = set()
    for p in observation.get("obstacles", []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    self_role = str(observation.get("self_role", "")).lower()
    is_pursuer = ("purs" in self_role) or ("evader" not in self_role)

    # Intercept heuristic for wall-run evasion:
    # Move toward the "inward" square next to the wall the opponent is hugging.
    tx, ty = ox, oy
    if ox <= 0:
        tx = 1
    elif ox >= w - 1:
        tx = w - 2
    if oy <= 0:
        ty = 1
    elif oy >= h - 1:
        ty = h - 2

    # If those inward squares are blocked, fall back to direct pursuit.
    if not inb(tx, ty):
        tx, ty = ox, oy
        if not inb(tx, ty):
            tx, ty = max(min(sx, w - 1), 0), max(min(sy, h - 1), 0)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        if is_pursuer:
            d_to_t = max(abs(nx - tx), abs(ny - ty))
            d_to_o = max(abs(nx - ox), abs(ny - oy))
            # Prefer getting closer to intercept; secondarily get closer to opponent;
            # finally avoid worsening distance to opponent.
            prog = max(abs(sx - ox), abs(sy - oy)) - d_to_o
            wall_pen = (1 if nx == 0 or nx == w - 1 else 0) + (1 if ny == 0 or ny == h - 1 else 0)
            key = (d_to_t, -prog, d_to_o, wall_pen)
        else:
            # If somehow evading, maximize distance from opponent and from intercept.
            d_to_t = max(abs(nx - tx), abs(ny - ty))
            d_to_o = max(abs(nx - ox), abs(ny - oy))
            key = (-d_to_o, -d_to_t, 0)

        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]