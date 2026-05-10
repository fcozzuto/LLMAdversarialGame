def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def role_is_evader():
        sr = str(observation.get("self_role") or "").lower()
        if "evader" in sr:
            return True
        if any(k in sr for k in ("pursuer", "chaser", "hunter")):
            return False
        # fallback: if unknown, assume we should be the pursuer to avoid 0/0 policy drift
        return False

    is_evader = role_is_evader()

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Deterministic target selection to resist zigzag symmetry
    # If evader: choose a corner far from pursuer with parity tie-break
    # If pursuer: choose a "near-corner" interception: move to reduce dist to chosen corner away from evader corner
    corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]
    parity = (ox + oy + observation["turn_index"]) % 2
    corners_sorted = sorted(corners, key=lambda c: (manh(c[0],c[1],ox,oy), ((c[0]+c[1])%2) != parity))
    if is_evader:
        tx, ty = corners_sorted[-1]
    else:
        # pursuer aims for farthest corner from opponent but tends toward it only to shepherd; prevents useless dithering
        tx, ty = corners_sorted[0]

    # One-step "prediction" for pursuer/evader: aim based on relative direction
    step_dx = 0 if ox == sx else (1 if ox > sx else -1)
    step_dy = 0 if oy == sy else (1 if oy > sy else -1)
    px, py = ox + (step_dx if is_evader else 0), oy + (step_dy if is_evader else 0)

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        d_opp = manh(nx, ny, ox, oy)
        d_target = manh(nx, ny, tx, ty)
        # Small tie-breakers to avoid oscillations: prefer moves that change parity in place (or reduce center stalling)
        center = ((nx - (w-1)/2.0)**2 + (ny - (h-1)/2.0)**2)
        # If role unknown, is_evader False already.
        if is_evader:
            val = (d_opp, -d_target, -(-center), -((nx+ny)&1))
        else:
            # pursuer: minimize distance to opponent primarily; secondary reduce distance to a shepherd target
            val = (-d_opp, d_target, -(-center), ((nx+ny)&1))
        if best is None or val > best_val:
            best = [dx, dy]
            best_val = val

    if best is not None:
        return best
    return [0, 0]