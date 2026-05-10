def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in observation.get("obstacles", []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))

    self_role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()
    is_self_pursuer = ("purs" in self_role) or ("purs" in opp_role) or ("evader" not in self_role)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        # Pursuer: minimize distance; Evader: maximize distance
        score = -d if is_self_pursuer else d
        # Small deterministic tie-break: prefer diagonal, then larger x delta, then larger y delta
        diag = 1 if dx != 0 and dy != 0 else 0
        tie = (diag, abs(dx), abs(dy), -nx, -ny)
        if best is None or score > best_score or (score == best_score and tie > best_tie):
            best = (dx, dy)
            best_score = score
            best_tie = tie

    if best is None:
        return [0, 0]
    return [best[0], best[1]]