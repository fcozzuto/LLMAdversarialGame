def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    x, y, ex, ey = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obs.add((int(a[0]), int(a[1])))

    role = str(observation.get("self_role", "")).lower()
    pursuer = ("pursuer" in role) or ("pursue" in role) or ("pursuit" in role) or role == "pursuer"

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def boundary_pen(nx, ny):
        b = min(nx, ny, (w - 1) - nx, (h - 1) - ny)
        return -b  # closer to edge is worse/better depending on sign in score

    # For evader: run to farthest corner; for pursuer: bias toward center-ish squares by chasing.
    if pursuer:
        target_x, target_y = ex, ey
    else:
        target_corner = max(corners, key=lambda c: abs(c[0] - ex) + abs(c[1] - ey))
        target_x, target_y = target_corner

    t = int(observation.get("turn_index", 0) or 0)
    preferred = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if t % 2 == 1:
        preferred = list(reversed(preferred))
    pref_rank = {d: i for i, d in enumerate(preferred)}

    best = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        d_to_opp = dist2(nx, ny, ex, ey)
        d_to_tgt = dist2(nx, ny, target_x, target_y)
        wall = boundary_pen(nx, ny)

        if pursuer:
            # primary: minimize distance to opponent; secondary: reduce distance to opponent corner direction; avoid getting stuck near edges
            score = (-d_to_opp * 1000) + (-d_to_tgt) + (wall * 0.5)
        else:
            # primary: maximize distance to opponent; secondary: increase distance to opponent from target direction; avoid edges
            score = (d_to_opp * 1000) + (d_to_tgt) + (-wall * 0.5)

        # deterministic tie-break
        if best is None or score > best or (score == best and pref_rank.get((dx, dy), 10**9) < pref_rank.get(best_move, 10**9)):
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]