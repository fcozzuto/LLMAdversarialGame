def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        x = a - c
        if x < 0:
            x = -x
        y = b - d
        if y < 0:
            y = -y
        return x + y

    def legal_moves(x, y):
        moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        out = []
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                out.append((dx, dy, nx, ny))
        return out

    def pick_resource(px, py):
        if not resources:
            return None
        best = None
        best_key = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            sd = dist(px, py, rx, ry)
            od = dist(ox, oy, rx, ry)
            lead = od - sd  # positive if we can arrive first
            # If we can arrive first, strongly prefer larger lead and smaller sd.
            # Otherwise, prefer denying the closest-to-opponent resource.
            can_beat = 1 if sd < od else 0
            key = (can_beat, lead, -sd if can_beat else -od, -rx, -ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry, sd, od, lead)
        return best

    if not resources:
        return [0, 0]

    moves = legal_moves(sx, sy)
    if not moves:
        return [0, 0]

    best_score = None
    best_move = [0, 0]
    # Two-tier evaluation: our next-step advantage on the resource we would target then.
    for dx, dy, nx, ny in moves:
        t = pick_resource(nx, ny)
        if t is None:
            sc = 0
        else:
            rx, ry, sd, od, lead = t
            # Encourage immediate collection if we land on a resource; also bias away from being late.
            on_res = 1 if (nx == rx and ny == ry) else 0
            sc = (on_res * 10**6) + (lead * 1000) - sd - (0 if sd < od else (sd - od) * 20)
            # Small deterministic tie-break: prefer moving "east/north" by coordinate
            sc += (-nx) * 0.001 + (-ny) * 0.0001
        if best_score is None or sc > best_score:
            best_score = sc
            best_move = [dx, dy]
    return best_move