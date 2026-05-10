def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    obstacles = observation.get("obstacles") or []
    obs = set((int(p[0]), int(p[1])) for p in obstacles)
    sr = (observation.get("self_role") or "").lower()
    orr = (observation.get("opponent_role") or "").lower()
    if "evad" in sr:
        i_am_pursuer = False
    elif "purs" in sr:
        i_am_pursuer = True
    else:
        i_am_pursuer = ("evad" not in orr)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    t = int(observation.get("turn_index", 0))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def score_cell(x, y):
        # local obstacle pressure: prefer cells with fewer nearby obstacles (deterministic, cheap)
        near = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obs:
                    near += 1
        dx = x - ox
        dy = y - oy
        d2 = dx * dx + dy * dy
        # wall/obstacle safety bias
        wall = min(x, y, w - 1 - x, h - 1 - y)
        wall_term = wall * 0.05
        if i_am_pursuer:
            # pursuer: minimize distance, but avoid bad local trapping near obstacles/walls
            return -d2 - 0.6 * near - 0.1 / (wall + 1e-9) - wall_term
        else:
            # evader: maximize distance, avoid obstacles and don't collapse into walls too much
            return d2 - 0.8 * near + 0.2 * wall_term + (0.001 * (t % 2))

    best = None
    best_score = None
    for k, (dx, dy) in enumerate(moves):
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        sc = score_cell(nx, ny)
        # deterministic tie-break using move index and time parity
        if best_score is None or sc > best_score or (sc == best_score and ((k + t) % 9) < ((best[2] + t) % 9)):
            best_score = sc
            best = (dx, dy, k)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]