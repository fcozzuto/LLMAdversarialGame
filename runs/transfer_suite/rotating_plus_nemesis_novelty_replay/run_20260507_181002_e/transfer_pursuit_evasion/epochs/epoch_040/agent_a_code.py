def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    sr = str(observation.get("self_role", "")).lower()
    self_is_evader = ("evader" in sr) or ("runner" in sr)
    if not self_is_evader:
        orr = str(observation.get("opponent_role", "")).lower()
        if ("evader" in orr) or ("runner" in orr):
            self_is_evader = False

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_score = -10**18 if self_is_evader else 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = dist(nx, ny, ox, oy)

        # Center pressure and mild anti-stalling to improve robustness against zigzags
        center = -((nx - cx) ** 2 + (ny - cy) ** 2)
        parity = 1 if ((nx + ny) & 1) == ((sx + sy) & 1) else 0  # deterministic small influence

        if self_is_evader:
            # maximize distance; prefer center-ish staying feasible; break ties by changing parity (zigzag resistance)
            score = d * 2000 + center * 0.5 + parity * 5 - (abs(dx) + abs(dy)) * 2
            better = score > best_score
        else:
            # minimize distance; if tied, prefer diagonal progress and moving toward center (avoid corner traps)
            score = d * 2000 - center * 0.5 + parity * 2 + (abs(dx) + abs(dy)) * 0.1
            better = score < best_score

        if best is None or better or (score == best_score and (dx, dy) < best):
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]