def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles", []) or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    role = str(observation.get("self_role", "") or "").lower()
    evader = "evader" in role

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    best_move = [0, 0]
    best_key = None

    # Direction sign to keep "cutting off" zigzags deterministically
    sdx = 0 if ox == sx else (1 if ox > sx else -1)
    sdy = 0 if oy == sy else (1 if oy > sy else -1)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if evader:
        # Farthest corner from opponent; helps avoid easy catches
        tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    else:
        tx, ty = ox, oy

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        md = abs(nx - ox) + abs(ny - oy)
        cd = max(abs(nx - ox), abs(ny - oy))
        # Encourage moving toward/away from target corner (evader) or opponent (pursuer)
        td = abs(nx - tx) + abs(ny - ty)
        # Prefer stepping in the general direction of the opponent (pursuer) / away (evader)
        align = (dx == sdx) + (dy == sdy) + (dx == -sdx) * 0 + (dy == -sdy) * 0
        if not evader:
            # Primary: minimize distance; Secondary: minimize Chebyshev (diagonal catches); Tertiary: closer to opponent
            key = (md, cd, td, -align, dx, dy)
        else:
            # Primary: maximize distance; Secondary: maximize Chebyshev; Tertiary: push toward farthest corner
            key = (-md, -cd, -td, -align, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    # If all neighbors blocked, stay
    if best_key is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]