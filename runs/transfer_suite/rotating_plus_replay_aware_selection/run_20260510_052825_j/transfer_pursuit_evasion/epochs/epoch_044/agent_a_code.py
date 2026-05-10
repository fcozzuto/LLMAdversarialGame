def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    opponent_role = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evad" in self_role) or (self_role == "evader") or ("purs" in opponent_role)
    self_is_pursuer = ("purs" in self_role) or (self_role == "pursuer")

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(a, b, c, d): return abs(a - c) + abs(b - d)

    # Deterministic move order (bias diagonals then orthogonal, then stay)
    deltas = [(-1, -1), (-1, 1), (1, -1), (1, 1), (0, -1), (-1, 0), (1, 0), (0, 1), (0, 0)]

    best = None
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue

        d = man(nx, ny, ox, oy)
        # Small tie-break: prefer moving to same parity as a corner path (deterministic)
        parity_bias = -((nx + ny) & 1) if ((sx + sy) & 1) == 0 else ((nx + ny) & 1)

        if self_is_pursuer:
            # Chase: minimize distance, but also avoid getting "boxed" by obstacles
            obs_adj = 0
            for ax, ay in obstacles:
                if man(nx, ny, ax, ay) <= 1:
                    obs_adj += 1
            score = (-d) * 10 - obs_adj + parity_bias
        else:
            # Evade: maximize distance, also prefer moving away from obstacles to keep options
            obs_adj = 0
            for ax, ay in obstacles:
                if man(nx, ny, ax, ay) <= 1:
                    obs_adj += 2
            score = (d) * 10 - obs_adj + parity_bias

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best