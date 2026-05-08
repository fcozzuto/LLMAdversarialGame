def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    self_role = observation.get('self_role', '')
    self_pos = observation.get('self_position', [0, 0])
    opp_pos = observation.get('opponent_position', [0, 0])
    obstacles = observation.get('obstacles', [])
    ox = set((p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) == 2)
    x0, y0 = int(self_pos[0]), int(self_pos[1])
    xo, yo = int(opp_pos[0]), int(opp_pos[1])

    moves = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    best_corner = max(corners, key=lambda c: (c[0] - xo) * (c[0] - xo) + (c[1] - yo) * (c[1] - yo))

    def in_bounds(x, y): return 0 <= x < w and 0 <= y < h

    want_pursuer = (self_role.lower() == 'pursuer')
    # If unsure, treat as evader when role isn't explicitly pursuer.
    if 'evader' in self_role.lower() or not want_pursuer:
        want_pursuer = False

    best = None
    best_val = None
    for dx, dy in moves:
        x, y = x0 + dx, y0 + dy
        if not in_bounds(x, y) or (x, y) in ox:
            continue
        d2 = (x - xo) * (x - xo) + (y - yo) * (y - yo)
        man = abs(x - xo) + abs(y - yo)
        center_bias = (x - (w - 1) / 2.0) * (x - (w - 1) / 2.0) + (y - (h - 1) / 2.0) * (y - (h - 1) / 2.0)
        corner_bias = (x - best_corner[0]) * (x - best_corner[0]) + (y - best_corner[1]) * (y - best_corner[1])
        # Obstacles handled by filtering; prefer staying legal.
        if want_pursuer:
            val = (-d2, man, center_bias, corner_bias)  # maximize tuple negative d2 -> minimize d2
        else:
            val = (d2, corner_bias, -center_bias, -man)  # maximize distance and corner bias
        if best is None or (val > best_val):
            best, best_val = (dx, dy), val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]