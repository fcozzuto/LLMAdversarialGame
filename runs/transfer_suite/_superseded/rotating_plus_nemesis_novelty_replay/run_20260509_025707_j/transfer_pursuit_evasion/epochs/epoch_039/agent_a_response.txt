def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("runner" in role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(x, y, a, b):
        return abs(x - a) + abs(y - b)

    def nearest_obstacle_clearance(x, y):
        if not obstacles:
            return 99
        md = 10**9
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < md:
                md = d
        return md if md != 10**9 else 99

    # Greedy one-step search with obstacle-aware tie-breaking
    best_move = (0, 0)
    best_score = None
    # Prefer moving away/toward with diagonal preserved; add anti-jitter based on turn_index parity
    parity = int(observation.get("turn_index", 0) or 0) & 1
    jitter_dir = (1 if parity == 0 else -1)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            score = -10**6 if evader else -10**6
        else:
            d_op = dist(nx, ny, ox, oy)
            clear = nearest_obstacle_clearance(nx, ny)
            # Small deterministic bias to encourage commitment to a direction
            bias = 0
            if dx == 0 and dy != 0:
                bias = 0.02 * (1 if dy == jitter_dir else -1)
            elif dy == 0 and dx != 0:
                bias = 0.02 * (1 if dx == jitter_dir else -1)
            elif dx != 0 and dy != 0:
                bias = 0.02 * (1 if (dx == dy and parity == 0) or (dx == -dy and parity == 1) else -1)

            if evader:
                # Maximize distance from opponent; avoid obstacles more strongly when close
                score = (d_op * 1.0) + (clear * 0.35) + bias
            else:
                # Pursuer: minimize distance to opponent; avoid obstacles
                score = (-d_op * 1.0) + (clear * 0.25) + bias

        if best_score is None or (evader and score > best_score) or ((not evader) and score > best_score):
            best_score = score
            best_move = (dx, dy)

        # Deterministic tie-break: if scores equal, pick lexicographically smaller (dx,dy) to stabilize
        elif best_score is not None and score == best_score:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]