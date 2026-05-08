def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def to_xy(obj):
        if isinstance(obj, (list, tuple)) and len(obj) == 2:
            return int(obj[0]), int(obj[1])
        if isinstance(obj, dict):
            q = obj.get("position", obj.get("pos", None))
            if isinstance(q, (list, tuple)) and len(q) == 2:
                return int(q[0]), int(q[1])
        return None

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        t = to_xy(p)
        if t is not None:
            obs_set.add(t)

    resources = []
    for r in observation.get("resources", []) or []:
        t = to_xy(r)
        if t is not None:
            resources.append(t)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny) and (nx, ny) not in obs_set:
            moves.append((dx, dy))
    if not moves:
        return [0, 0]

    best = None
    best_val = None
    near_cut = 2  # strongly prefer capturing adjacent resource
    for dx, dy in sorted(moves):
        nx, ny = sx + dx, sy + dy
        # Resource value
        if (nx, ny) in resources:
            val = 10000
        else:
            if resources:
                dres = min(man(nx, ny, rx, ry) for rx, ry in resources)
                # If opponent can likely reach a nearby resource sooner, penalize
                # (approx: compare distances to nearest resource)
                dop = min(man(ox, oy, rx, ry) for rx, ry in resources)
                dopp_next = min(man(ox, oy, rx, ry) for rx, ry in resources)  # deterministic placeholder
                # Encourage moving toward resources; discourage if opponent already much closer
                closer_pen = 0
                if dres <= near_cut and dop <= dres:
                    closer_pen = 500
                val = -dres * 10 - closer_pen
            else:
                val = 0

        # Opponent distancing (tie-breaker / safety)
        dop_move = man(nx, ny, ox, oy)
        val += dop_move * 1.5
        # Slightly prefer progressing toward the center line when resources are absent
        if not resources:
            center_bias = -abs(nx - (w - 1) / 2) * 0.1 - abs(ny - (h - 1) / 2) * 0.1
            val += center_bias

        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]
    return best