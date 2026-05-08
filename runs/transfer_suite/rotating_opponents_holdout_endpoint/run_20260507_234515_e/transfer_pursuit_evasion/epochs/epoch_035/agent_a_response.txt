def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role", "") or "").lower()
    self_pursuer = ("purs" in role) or (("direct" in role) and ("evad" not in role)) or (role == "")
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x, y, a, b):
        return abs(x - a) + abs(y - b)

    # If pursuer: minimize distance; strongly prefer capture move.
    # If evader: maximize distance; prefer moving toward farthest corner; avoid obstacles.
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in oset:
            continue
        d_now = manh(sx, sy, ox, oy)
        d_next = manh(nx, ny, ox, oy)
        if self_pursuer:
            if nx == ox and ny == oy:
                score = 10_000_000 - (dx == 0 and dy == 0) * 10
            else:
                # chase and align: reduce distance most; slight penalty for staying
                score = -d_next * 1000 - (d_now - d_next) * 5 - (dx == 0 and dy == 0) * 3
                # avoid getting too close to obstacles? light penalty if next is adjacent to many obstacles
                adj = 0
                for ax in (-1, 0, 1):
                    for ay in (-1, 0, 1):
                        if ax == 0 and ay == 0:
                            continue
                        tx, ty = nx + ax, ny + ay
                        if (tx, ty) in oset:
                            adj += 1
                score -= adj * 2
        else:
            if nx == ox and ny == oy:
                score = -10_000_000
            else:
                corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
                far_corner = -10**9
                for cx, cy in corners:
                    dc = manh(nx, ny, cx, cy)
                    far_corner = max(far_corner, dc)
                # maximize distance from opponent; also prefer far-from-centre by biasing toward corners
                score = d_next * 1200 + far_corner * 3 + (d_next > d_now) * 8
                # avoid being trapped near obstacles: penalize adjacency
                adj = 0
                for ax in (-1, 0, 1):
                    for ay in (-1, 0, 1):
                        if ax == 0 and ay == 0:
                            continue
                        tx, ty = nx + ax, ny + ay
                        if (tx, ty) in oset:
                            adj += 1
                score -= adj * 6
                # slight preference to keep moving (reduce oscillation)
                score -= (dx == 0 and dy == 0) * 2
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best